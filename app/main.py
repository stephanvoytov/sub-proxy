import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.backends import get_backend
from app.cache import state
from app.services.merger import merge_subscription
from app.services.refresher import refresh_cache, start_refresher


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_refresher())
    yield


app = FastAPI(title="Sub-Proxy", version="2.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "cache_groups": len(state.BYPASS_CACHE),
        "cache_entries": sum(len(v) for v in state.BYPASS_CACHE.values()),
        "last_refresh": state.LAST_REFRESH,
        "sources": len(settings.sources),
    }


@app.get("/api/refresh")
async def refresh():
    await refresh_cache()
    return {"status": "ok", "groups": len(state.BYPASS_CACHE)}


@app.get("/api/status")
async def status():
    return {
        "sources": [
            {"label": s.label, "url": s.url, "count": s.count, "probe": s.probe}
            for s in settings.sources
        ],
        "cache": {
            label: len(entries)
            for label, entries in state.BYPASS_CACHE.items()
        },
        "probed": len(state.PROBE_RESULTS),
        "last_refresh": state.LAST_REFRESH,
    }


@app.api_route("/{short_uuid:path}", methods=["GET", "POST"])
async def sub(short_uuid: str, request: Request):
    user_agent = request.headers.get("User-Agent", "")
    hw_id = request.headers.get("x-hwid", "")

    backend = get_backend()

    try:
        extra_headers = {}
        if hw_id:
            extra_headers["x-hwid"] = hw_id

        original = await backend.fetch_subscription(
            short_uuid=short_uuid,
            user_agent=user_agent,
            headers=extra_headers,
        )
    except Exception as e:
        return PlainTextResponse(f"Backend error: {e}", status_code=502)

    if state.BYPASS_CACHE:
        source_order = [s.label for s in settings.sources]
        merged = merge_subscription(
            original=original,
            sources=state.BYPASS_CACHE,
            source_order=source_order,
            dedup=settings.DEDUP_ENABLED,
            probed=state.PROBE_RESULTS,
        )
        return Response(
            content=merged,
            media_type="text/plain",
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Profile-Title": "Sub-Proxy Merged",
            },
        )

    return Response(
        content=original,
        media_type="text/plain",
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "Profile-Title": "Sub-Proxy",
        },
    )

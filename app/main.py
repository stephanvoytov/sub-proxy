import asyncio
import base64
import re
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.cache import state
from app.services.merger import merge_subscription
from app.services.refresher import refresh_cache, start_refresher

PROTOCOLS = (b"vless://", b"vmess://", b"ss://", b"hysteria2://", b"trojan://")
SHORT_UUID_RE = re.compile(r"^[A-Za-z0-9_\-]{8,32}$")

# Shared HTTP client with connection pooling
_client: httpx.AsyncClient | None = None
_SUB_CACHE: dict[str, tuple[float, bytes]] = {}
_SUB_CACHE_TTL = 30  # seconds


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)
        _client = httpx.AsyncClient(timeout=20, follow_redirects=False, limits=limits)
    return _client


async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None


def looks_like_subscription(body: bytes) -> bool:
    try:
        decoded = base64.b64decode(body + b"==").decode("utf-8", errors="ignore")
        return any(p.decode() in decoded for p in PROTOCOLS)
    except Exception:
        return False


def extract_short_uuid(path: str) -> str | None:
    parts = [p for p in path.strip("/").split("/") if p]
    if not parts:
        return None
    candidate = parts[-1]
    if SHORT_UUID_RE.match(candidate):
        return candidate
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_refresher())
    yield
    await close_client()


app = FastAPI(title="Sub-Proxy", version="3.0.0", lifespan=lifespan)


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


@app.api_route("/{path:path}", methods=["GET", "HEAD", "POST"])
async def proxy(path: str, request: Request):
    upstream_url = f"{settings.BACKEND_URL.rstrip('/')}/{path}"
    if request.url.query:
        upstream_url += f"?{request.url.query}"

    short_uuid = None
    # Check subscription cache (GET only, subscription-like paths)
    cache_key = upstream_url
    if request.method == "GET":
        short_uuid = extract_short_uuid(path)
        if short_uuid:
            cached = _SUB_CACHE.get(short_uuid)
            if cached and time.time() - cached[0] < _SUB_CACHE_TTL:
                return Response(
                    content=cached[1],
                    status_code=200,
                    media_type="text/plain; charset=utf-8",
                    headers={"content-length": str(len(cached[1]))},
                )

    forward_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "accept-encoding")
    }
    forward_headers["accept-encoding"] = "identity"
    body_bytes = await request.body()

    try:
        client = get_client()
        upstream = await client.request(
            method=request.method,
            url=upstream_url,
            headers=forward_headers,
            content=body_bytes,
        )
    except Exception as exc:
        return PlainTextResponse(f"upstream error: {exc}", status_code=502)

    body = upstream.content
    content_type = upstream.headers.get("content-type", "")
    is_plain = "text/plain" in content_type or "octet-stream" in content_type

    if request.method == "GET" and is_plain and looks_like_subscription(body):
        if short_uuid and state.BYPASS_CACHE:
            source_order = [s.label for s in settings.sources]

            # Filter sources by squad
            filtered_cache = {}
            for label in source_order:
                entries = state.BYPASS_CACHE.get(label, [])
                if not entries:
                    continue
                src = next((s for s in settings.sources if s.label == label), None)
                if src and src.squads and short_uuid not in src.squads:
                    continue  # source restricted to other squads
                filtered_cache[label] = entries

            if filtered_cache:
                merged = merge_subscription(
                    original=body,
                    sources=filtered_cache,
                    source_order=source_order,
                    dedup=settings.DEDUP_ENABLED,
                    probed=state.PROBE_RESULTS,
                )
                body = merged
                # Cache the merged result
                _SUB_CACHE[short_uuid] = (time.time(), body)

    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    resp_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in excluded
    }
    resp_headers["content-length"] = str(len(body))

    return Response(
        content=body,
        status_code=upstream.status_code,
        headers=resp_headers,
        media_type=content_type or "application/octet-stream",
    )

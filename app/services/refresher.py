import asyncio
import time
from app.config import settings
from app.cache import state
from app.services.fetcher import fetch_all_sources
from app.services.dedup import deduplicate


async def refresh_cache():
    print("REFRESH | starting cache refresh...")

    try:
        sources = settings.sources
        if not sources:
            print("REFRESH | no sources configured, skipping")
            return

        fetched = await fetch_all_sources(sources)

        for label, entries in fetched.items():
            if settings.DEDUP_ENABLED:
                entries = deduplicate(entries)
            state.BYPASS_CACHE[label] = entries
            print(f"REFRESH | label={label} | count={len(entries)}")

        state.LAST_REFRESH = time.time()
        print(f"REFRESH | done, total groups={len(fetched)}")

    except Exception as e:
        print(f"REFRESH | error: {e}")


async def start_refresher():
    await refresh_cache()

    while True:
        await asyncio.sleep(settings.REFRESH_INTERVAL)
        await refresh_cache()

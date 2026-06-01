import asyncio
import socket
from typing import Dict, List
from app.models import ServerEntry
from app.cache import state


async def probe_server(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def probe_all_entries(timeout: float = 1.5, concurrency: int = 12) -> Dict[str, bool]:
    all_entries: List[ServerEntry] = []
    for entries in state.BYPASS_CACHE.values():
        all_entries.extend(entries)

    sem = asyncio.Semaphore(concurrency)

    async def probe_with_sem(entry: ServerEntry) -> tuple[str, bool]:
        async with sem:
            ok = await probe_server(entry.host, entry.port, timeout)
            return entry.raw, ok

    results = await asyncio.gather(*[probe_with_sem(e) for e in all_entries])

    probed: Dict[str, bool] = {}
    for raw, ok in results:
        probed[raw] = ok

    state.PROBE_RESULTS = probed
    return probed

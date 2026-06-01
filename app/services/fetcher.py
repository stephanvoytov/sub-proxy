from typing import Dict, List
from app.config import SourceConfig, settings
from app.providers.url import UrlProvider
from app.models import ServerEntry


async def fetch_all_sources(sources: List[SourceConfig]) -> Dict[str, List[ServerEntry]]:
    provider = UrlProvider()
    result: Dict[str, List[ServerEntry]] = {}

    for src in sources:
        entries = await provider.fetch(label=src.label, url=src.url)
        if src.count > 0:
            entries = entries[:src.count]
        result[src.label] = entries

    return result

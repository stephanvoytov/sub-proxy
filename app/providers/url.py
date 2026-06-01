import base64
from typing import List
import httpx
from app.providers.base import ProviderBase
from app.models import ServerEntry
from app.services.parser import parse_config


class UrlProvider(ProviderBase):
    async def fetch(self, label: str, url: str = "") -> List[ServerEntry]:
        if not url:
            return []

        entries = []
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                body = resp.text

                try:
                    decoded = base64.b64decode(body + "==").decode("utf-8", errors="ignore")
                    if "://" in decoded:
                        lines = decoded.splitlines()
                    else:
                        lines = body.splitlines()
                except Exception:
                    lines = body.splitlines()

                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    entry = parse_config(line)
                    if entry:
                        entry.source_label = label
                        entry.source = url
                        entries.append(entry)
        except Exception as e:
            print(f"PROVIDER FAILED | label={label} | url={url} | {e}")

        return entries

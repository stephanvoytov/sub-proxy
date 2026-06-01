from typing import List
from app.providers.base import ProviderBase
from app.models import ServerEntry
from app.services.parser import parse_config


class LocalProvider(ProviderBase):
    async def fetch(self, label: str, path: str = "") -> List[ServerEntry]:
        if not path:
            return []

        entries = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    entry = parse_config(line)
                    if entry:
                        entry.source_label = label
                        entry.source = path
                        entries.append(entry)
        except Exception as e:
            print(f"LOCAL PROVIDER FAILED | label={label} | path={path} | {e}")

        return entries

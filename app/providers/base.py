from abc import ABC, abstractmethod
from typing import List
from app.models import ServerEntry


class ProviderBase(ABC):
    @abstractmethod
    async def fetch(self, label: str) -> List[ServerEntry]:
        ...

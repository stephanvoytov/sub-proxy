from abc import ABC, abstractmethod


class BackendBase(ABC):
    @abstractmethod
    async def fetch_subscription(self, short_uuid: str, user_agent: str = "", headers: dict = None) -> bytes:
        ...

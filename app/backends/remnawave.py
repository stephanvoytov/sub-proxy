import httpx
from app.backends.base import BackendBase
from app.config import settings


class RemnawaveBackend(BackendBase):
    def __init__(self):
        self.base_url = settings.BACKEND_URL.rstrip("/")
        self.api_token = settings.BACKEND_API_TOKEN

    async def fetch_subscription(self, short_uuid: str, user_agent: str = "", headers: dict = None) -> bytes:
        url = f"{self.base_url}/api/sub/{short_uuid}"

        req_headers = {
            "User-Agent": user_agent or "sub-proxy/2.0",
            "Accept": "*/*",
        }
        if self.api_token:
            req_headers["x-hwid"] = self.api_token

        if headers:
            req_headers.update(headers)

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=req_headers)
            resp.raise_for_status()
            return resp.content

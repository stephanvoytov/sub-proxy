import httpx


COUNTRY_CACHE: dict[str, str] = {}


async def detect_country(ip: str) -> str:
    if not ip:
        return ""

    if ip in COUNTRY_CACHE:
        return COUNTRY_CACHE[ip]

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=countryCode")
            if resp.status_code == 200:
                data = resp.json()
                code = data.get("countryCode", "")
                COUNTRY_CACHE[ip] = code
                return code
    except Exception:
        pass

    return ""

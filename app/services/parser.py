from urllib.parse import urlparse, parse_qs, unquote
from app.models import ServerEntry


def parse_config(raw: str) -> ServerEntry | None:
    if not raw or "://" not in raw:
        return None

    if raw.startswith("divider://"):
        return None

    try:
        protocol = raw.split("://")[0]
        if not protocol:
            return None
        rest = raw[len(protocol) + 3:]

        name = ""
        if "#" in rest:
            rest, name_part = rest.rsplit("#", 1)
            name = unquote(name_part).strip()

        host = ""
        port = 0
        uuid = ""
        security = ""
        network = "tcp"

        if "@" in rest:
            uuid_part, addr_part = rest.split("@", 1)
            uuid = uuid_part
            if ":" in addr_part:
                host, port_str = addr_part.rsplit(":", 1)
                if "?" in port_str:
                    port_str, _ = port_str.split("?", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    host = addr_part
            else:
                host = addr_part
        else:
            parsed = urlparse(raw)
            host = parsed.hostname or ""
            try:
                port = parsed.port or 0
            except ValueError:
                port = 0
            uuid = parsed.username or ""
            qs = parse_qs(parsed.query)
            security = qs.get("security", [""])[0]
            network = qs.get("type", [""])[0] or qs.get("network", [""])[0]

        if raw.startswith("vless://"):
            params_str = rest.split("?")[1] if "?" in rest else ""
            params = parse_qs(params_str) if params_str else {}
            security = params.get("security", [""])[0]
            network = params.get("type", [""])[0] or params.get("network", [""])[0]

        return ServerEntry(
            raw=raw,
            protocol=protocol,
            host=host,
            port=port,
            uuid=uuid,
            security=security,
            network=network,
            name=name,
        )
    except Exception:
        return None

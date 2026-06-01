from dataclasses import dataclass, field


@dataclass
class ServerEntry:
    raw: str
    protocol: str = ""
    host: str = ""
    port: int = 0
    uuid: str = ""
    security: str = ""
    network: str = ""
    name: str = ""
    country: str = ""
    source_label: str = ""
    is_blacklisted: bool = False
    source: str = ""
    is_dividier: bool = False

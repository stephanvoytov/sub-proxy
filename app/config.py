from pydantic_settings import BaseSettings
from typing import Dict, List


class SourceConfig(BaseSettings):
    label: str
    url: str
    count: int = 10
    probe: bool = False


class Settings(BaseSettings):
    # Backend
    BACKEND_TYPE: str = "remnawave"
    BACKEND_URL: str = ""
    BACKEND_API_TOKEN: str = ""

    # Custom sources: SOURCE_1_LABEL, SOURCE_1_URL, SOURCE_1_COUNT, SOURCE_1_PROBE
    # Format: SOURCE_{ID}_{FIELD}
    SOURCE_1_LABEL: str = ""
    SOURCE_1_URL: str = ""
    SOURCE_1_COUNT: int = 10
    SOURCE_1_PROBE: bool = False

    SOURCE_2_LABEL: str = ""
    SOURCE_2_URL: str = ""
    SOURCE_2_COUNT: int = 10
    SOURCE_2_PROBE: bool = False

    SOURCE_3_LABEL: str = ""
    SOURCE_3_URL: str = ""
    SOURCE_3_COUNT: int = 10
    SOURCE_3_PROBE: bool = False

    SOURCE_4_LABEL: str = ""
    SOURCE_4_URL: str = ""
    SOURCE_4_COUNT: int = 10
    SOURCE_4_PROBE: bool = False

    SOURCE_5_LABEL: str = ""
    SOURCE_5_URL: str = ""
    SOURCE_5_COUNT: int = 10
    SOURCE_5_PROBE: bool = False

    # Behaviour
    REFRESH_INTERVAL: int = 900
    PROBE_TIMEOUT: float = 1.5
    PROBE_CONCURRENCY: int = 12
    PROBE_SAMPLE_SIZE: int = 120
    DEDUP_ENABLED: bool = True

    SQUAD_CACHE_TTL: int = 300

    SNAPSHOT_PATH: str = "/data/cache.json"

    model_config = {"env_file": ".env"}

    @property
    def sources(self) -> List[SourceConfig]:
        result = []
        for i in range(1, 6):
            label = getattr(self, f"SOURCE_{i}_LABEL", "")
            url = getattr(self, f"SOURCE_{i}_URL", "")
            if label and url:
                result.append(SourceConfig(
                    label=label,
                    url=url,
                    count=getattr(self, f"SOURCE_{i}_COUNT", 10),
                    probe=getattr(self, f"SOURCE_{i}_PROBE", False),
                ))
        return result


settings = Settings()

from typing import Dict, List
from app.models import ServerEntry


BYPASS_CACHE: Dict[str, List[ServerEntry]] = {}
PROBE_RESULTS: Dict[str, bool] = {}
LAST_REFRESH: float = 0.0

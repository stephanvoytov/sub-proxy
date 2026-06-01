from app.backends.remnawave import RemnawaveBackend
from app.backends.simple import SimpleBackend


def get_backend(backend_type: str = ""):
    if not backend_type:
        from app.config import settings
        backend_type = settings.BACKEND_TYPE

    if backend_type == "remnawave":
        return RemnawaveBackend()
    return SimpleBackend()

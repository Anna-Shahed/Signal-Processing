from __future__ import annotations

import importlib
import pkgutil
from typing import Any

_CACHE: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """Resolve any public name by scanning this package's submodules lazily.

    Never imports at module load, so circular imports are impossible.
    """
    if name in _CACHE:
        return _CACHE[name]
    if name.startswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    for info in pkgutil.iter_modules(__path__):
        try:
            module = importlib.import_module(f"{__name__}.{info.name}")
        except Exception:
            continue
        attr = getattr(module, name, None)
        if attr is not None:
            _CACHE[name] = attr
            return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

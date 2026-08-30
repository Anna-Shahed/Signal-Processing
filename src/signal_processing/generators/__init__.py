from __future__ import annotations

import importlib
import pkgutil
from typing import Any

__all__ = [
    "chirp",
    "composite",
    "cosine",
    "gaussian_noise",
    "sawtooth",
    "sine",
    "square",
    "triangle",
    "white_noise",
]

_CACHE: dict[str, Any] = {}

def __getattr__(name: str) -> Any:
    """Lazily resolve public names from the generators submodules.

    Avoids the circular self-import caused by a static
    ``from signal_processing.generators import ...`` line inside the
    package's own __init__.
    """
    if name in _CACHE:
        return _CACHE[name]
    if name in __all__:
        for info in pkgutil.iter_modules(__path__):
            module = importlib.import_module(f"{__name__}.{info.name}")
            attr = getattr(module, name, None)
            if attr is not None:
                _CACHE[name] = attr
                return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

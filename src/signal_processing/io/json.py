"""JSON serialization for core data structures.

Numpy arrays are preserved losslessly via a ``__ndarray__`` type tag, so
metadata is never silently discarded on the round trip.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ..core import AnalysisResult, Event, Signal, Spectrogram, Spectrum


def _encode(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return {
            "__ndarray__": True,
            "dtype": str(obj.dtype),
            "shape": list(obj.shape),
            "data": obj.tolist(),
        }
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, (Signal, Spectrum, Spectrogram, Event, AnalysisResult)):
        return obj.to_dict()
    if isinstance(obj, dict):
        return {str(k): _encode(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_encode(v) for v in obj]
    return obj


def _decode(obj: Any) -> Any:
    if isinstance(obj, dict):
        if obj.get("__ndarray__") is True:
            return np.asarray(obj["data"], dtype=obj.get("dtype"))
        return {k: _decode(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decode(v) for v in obj]
    return obj


def to_json_string(obj: Any, *, indent: int = 2) -> str:
    """Serialize any laboratory object to a JSON string."""
    return json.dumps(_encode(obj), indent=indent, ensure_ascii=False)


def write_json(obj: Any, path: str | Path, *, indent: int = 2) -> Path:
    """Serialize an object to a JSON file, preserving arrays and metadata."""
    out = Path(path)
    if out.suffix.lower() != ".json":
        out = out.with_suffix(".json")
    try:
        out.write_text(to_json_string(obj, indent=indent), encoding="utf-8")
    except OSError as exc:  # pragma: no cover - environment dependent
        raise IOError(f"Failed to write JSON to {out}: {exc}") from exc
    return out


def read_json(path: str | Path) -> Any:
    """Read a JSON file produced by :func:`write_json`."""
    out = Path(path)
    if not out.is_file():
        raise FileNotFoundError(f"JSON file not found: {out}")
    return _decode(json.loads(out.read_text(encoding="utf-8")))


def signal_from_json(path: str | Path) -> Signal:
    """Read a JSON file and reconstruct a :class:`Signal`."""
    return Signal.from_dict(read_json(path))

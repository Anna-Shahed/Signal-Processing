"""Reusable result abstraction for analytical operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np


def _json_compatible(value: Any) -> Any:
    """Convert common scientific Python values to JSON-compatible values."""
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {
                "real": value.real.tolist(),
                "imag": value.imag.tolist(),
            }
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_compatible(item) for item in value]
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _json_compatible(value.to_dict())
    return value


@dataclass(slots=True)
class AnalysisResult:
    """Container for metrics, arrays, metadata, and analytical warnings."""

    metrics: dict[str, Any] = field(default_factory=dict)
    arrays: dict[str, np.ndarray] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.metrics = dict(self.metrics)
        self.arrays = {
            str(name): np.asarray(values) for name, values in self.arrays.items()
        }
        self.metadata = dict(self.metadata)
        self.warnings = [str(warning) for warning in self.warnings]

    def add_metric(self, name: str, value: Any) -> AnalysisResult:
        """Add or replace a named scalar or structured metric."""
        self.metrics[str(name)] = value
        return self

    def add_array(self, name: str, values: Any) -> AnalysisResult:
        """Add or replace a named NumPy array."""
        self.arrays[str(name)] = np.asarray(values)
        return self

    def warn(self, message: str) -> AnalysisResult:
        """Append a warning and return this result for fluent use."""
        self.warnings.append(str(message))
        return self

    def summary(self) -> str:
        """Return a compact human-readable summary."""
        lines = ["AnalysisResult"]
        if self.metrics:
            lines.append("Metrics:")
            lines.extend(f"  - {name}: {value}" for name, value in self.metrics.items())
        if self.arrays:
            lines.append("Arrays:")
            lines.extend(f"  - {name}: shape={array.shape}, dtype={array.dtype}"
                         for name, array in self.arrays.items())
        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"  - {warning}" for warning in self.warnings)
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the complete result without silently dropping arrays."""
        return {
            "metrics": _json_compatible(self.metrics),
            "arrays": {
                name: _json_compatible(values) for name, values in self.arrays.items()
            },
            "metadata": _json_compatible(self.metadata),
            "warnings": list(self.warnings),
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize the result to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalysisResult:
        """Construct a result from serialized data."""
        return cls(
            metrics=data.get("metrics", {}),
            arrays={
                name: np.asarray(values) for name, values in data.get("arrays", {}).items()
            },
            metadata=data.get("metadata", {}),
            warnings=data.get("warnings", []),
        )

    @classmethod
    def from_json(cls, text: str) -> AnalysisResult:
        """Construct a result from JSON text."""
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("AnalysisResult JSON must contain an object.")
        return cls.from_dict(data)

"""Validation helpers and public package exceptions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np


class SignalProcessingError(Exception):
    """Base exception for the signal-processing package."""


class SignalValidationError(SignalProcessingError, ValueError):
    """Raised when a signal or signal parameter is invalid."""


class TransformError(SignalProcessingError, ValueError):
    """Raised when a transform cannot be computed."""


class FilterDesignError(SignalProcessingError, ValueError):
    """Raised when filter specifications are invalid."""


class PipelineError(SignalProcessingError, RuntimeError):
    """Raised when a pipeline stage fails."""


class SignalIOError(SignalProcessingError, OSError):
    """Raised when reading or writing a signal fails."""


def validate_sampling_rate(sampling_rate: float) -> float:
    """Return a validated positive finite sampling rate."""
    rate = float(sampling_rate)
    if not np.isfinite(rate) or rate <= 0:
        raise SignalValidationError("sampling_rate must be finite and greater than zero.")
    return rate


def validate_real_array(
    values: Any,
    *,
    name: str = "values",
    dimensions: tuple[int, ...] = (1, 2),
) -> np.ndarray:
    """Convert values to a finite floating-point NumPy array."""
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise SignalValidationError(f"{name} must contain numeric values.") from exc

    if array.ndim not in dimensions:
        allowed = ", ".join(str(dimension) for dimension in dimensions)
        raise SignalValidationError(
            f"{name} must have one of the following dimensions: {allowed}."
        )
    if array.size == 0:
        raise SignalValidationError(f"{name} must not be empty.")
    if not np.all(np.isfinite(array)):
        raise SignalValidationError(f"{name} must contain only finite values.")
    return array


def validate_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    """Copy metadata into a plain dictionary."""
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise SignalValidationError("metadata must be a mapping.")
    return dict(metadata)

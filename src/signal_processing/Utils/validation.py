"""Validation helpers and public exceptions for the signal-processing package."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np


class SignalProcessingError(Exception):
    """Base exception for the signal-processing package."""


class SignalValidationError(SignalProcessingError, ValueError):
    """Raised when signal data or signal parameters are invalid."""


class TransformError(SignalProcessingError, ValueError):
    """Raised when a signal transform cannot be computed."""


class FilterDesignError(SignalProcessingError, ValueError):
    """Raised when filter specifications are invalid."""


class PipelineError(SignalProcessingError, RuntimeError):
    """Raised when a processing pipeline or one of its stages fails."""


class SignalIOError(SignalProcessingError, OSError):
    """Raised when reading or writing signal data fails."""


def validate_sampling_rate(sampling_rate: float) -> float:
    """
    Validate and normalize a signal sampling rate.

    A valid sampling rate must be a finite, strictly positive number.
    """
    try:
        rate = float(sampling_rate)
    except (TypeError, ValueError) as exc:
        raise SignalValidationError(
            "sampling_rate must be a numeric value."
        ) from exc

    if not np.isfinite(rate) or rate <= 0:
        raise SignalValidationError(
            "sampling_rate must be finite and greater than zero."
        )

    return rate


def validate_real_array(
    values: Any,
    *,
    name: str = "values",
    dimensions: tuple[int, ...] = (1, 2),
) -> np.ndarray:
    """
    Convert input data to a finite floating-point NumPy array.

    Parameters
    ----------
    values:
        Input data that can be converted to a NumPy array.
    name:
        Human-readable name used in validation error messages.
    dimensions:
        Allowed number of dimensions.

    Returns
    -------
    numpy.ndarray
        A finite floating-point NumPy array.

    Raises
    ------
    SignalValidationError
        If the input is invalid or contains non-finite values.
    """
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise SignalValidationError(
            f"{name} must contain numeric values."
        ) from exc

    if array.ndim not in dimensions:
        allowed = ", ".join(str(dimension) for dimension in dimensions)
        raise SignalValidationError(
            f"{name} must have one of the following dimensions: {allowed}."
        )

    if array.size == 0:
        raise SignalValidationError(f"{name} must not be empty.")

    if not np.all(np.isfinite(array)):
        raise SignalValidationError(
            f"{name} must contain only finite values."
        )

    return array


def validate_metadata(
    metadata: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate and copy metadata into a standard dictionary."""
    if metadata is None:
        return {}

    if not isinstance(metadata, Mapping):
        raise SignalValidationError(
            "metadata must be a mapping."
        )

    return dict(metadata)

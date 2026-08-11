"""Signal normalization utilities."""

from __future__ import annotations

import numpy as np

from ..core import Signal
from ..utils.validation import SignalValidationError


def normalize_peak(
    signal: Signal | np.ndarray,
    target: float = 1.0,
    *,
    sampling_rate: float | None = None,
) -> Signal:
    """Scale a signal so its peak absolute amplitude equals ``target``."""
    target = float(target)
    if not np.isfinite(target) or target <= 0:
        raise SignalValidationError("target must be finite and greater than zero.")

    if isinstance(signal, Signal):
        samples = signal.samples
        rate = signal.sampling_rate
        start_time = signal.start_time
    else:
        samples = np.asarray(signal, dtype=float)
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when normalizing a plain array."
            )
        rate = float(sampling_rate)
        start_time = 0.0

    peak = float(np.max(np.abs(samples)))
    if peak == 0:
        raise SignalValidationError("Cannot normalize an all-zero signal.")
    if not np.isfinite(peak):
        raise SignalValidationError("Input must contain finite values.")

    return Signal(
        samples=samples * (target / peak),
        sampling_rate=rate,
        start_time=start_time,
        name=signal.name if isinstance(signal, Signal) else "peak_normalized",
        metadata={"operation": "normalize_peak", "target": target, "scale": target / peak},
    )


def normalize_rms(
    signal: Signal | np.ndarray,
    target: float = 1.0,
    *,
    sampling_rate: float | None = None,
) -> Signal:
    """Scale a signal so its RMS amplitude equals ``target``."""
    target = float(target)
    if not np.isfinite(target) or target <= 0:
        raise SignalValidationError("target must be finite and greater than zero.")

    if isinstance(signal, Signal):
        samples = signal.samples
        rate = signal.sampling_rate
        start_time = signal.start_time
    else:
        samples = np.asarray(signal, dtype=float)
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when normalizing a plain array."
            )
        rate = float(sampling_rate)
        start_time = 0.0

    rms = float(np.sqrt(np.mean(np.square(samples))))
    if rms == 0:
        raise SignalValidationError("Cannot normalize an all-zero signal.")
    if not np.isfinite(rms):
        raise SignalValidationError("Input must contain finite values.")

    return Signal(
        samples=samples * (target / rms),
        sampling_rate=rate,
        start_time=start_time,
        name=signal.name if isinstance(signal, Signal) else "rms_normalized",
        metadata={"operation": "normalize_rms", "target": target, "scale": target / rms},
    )

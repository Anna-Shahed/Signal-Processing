"""Windowing operations for analysis and filtering."""

from __future__ import annotations

import numpy as np

from ..core import Signal
from ..filters.windows import get_window
from ..utils.validation import SignalValidationError


def apply_window(
    signal: Signal | np.ndarray,
    window: str | tuple[str, float] | np.ndarray,
    *,
    sampling_rate: float | None = None,
    name: str = "windowed",
) -> Signal:
    """Apply an analysis window to a signal.

    Windowing before an FFT reduces spectral leakage at the cost of wider
    main-lobe width and lower effective resolution.
    """
    if isinstance(signal, Signal):
        samples = signal.samples
        rate = signal.sampling_rate
        start_time = signal.start_time
        source_name = signal.name
    else:
        samples = np.asarray(signal, dtype=float)
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when windowing a plain array."
            )
        rate = float(sampling_rate)
        start_time = 0.0
        source_name = None

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Windowing requires a non-empty one-dimensional input.")

    window_values = get_window(window, samples.size)
    return Signal(
        samples=samples * window_values,
        sampling_rate=rate,
        start_time=start_time,
        name=name or (f"{source_name}_windowed" if source_name else "windowed"),
        metadata={
            "operation": "apply_window",
            "window": window,
            "length": samples.size,
        },
    )

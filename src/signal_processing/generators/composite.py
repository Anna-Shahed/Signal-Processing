"""Composition utilities for combining generated signals."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from ..core import Signal
from ..utils.validation import SignalValidationError


def composite(
    *signals: Signal,
    name: str = "composite",
    metadata: dict[str, object] | None = None,
) -> Signal:
    """Add multiple compatible signals sample by sample."""
    if not signals:
        raise SignalValidationError("At least one signal is required.")

    if any(not isinstance(signal, Signal) for signal in signals):
        raise SignalValidationError("All inputs must be Signal instances.")

    reference = signals[0]
    for signal in signals[1:]:
        if not np.isclose(signal.sampling_rate, reference.sampling_rate):
            raise SignalValidationError(
                "All signals must have the same sampling rate."
            )
        if signal.samples.shape != reference.samples.shape:
            raise SignalValidationError(
                "All signals must have the same sample shape."
            )
        if not np.isclose(signal.start_time, reference.start_time):
            raise SignalValidationError(
                "All signals must have the same start_time."
            )

    samples = np.sum(
        np.stack([signal.samples for signal in signals], axis=0),
        axis=0,
    )
    combined_metadata: dict[str, object] = {
        "generator": "composite",
        "components": [signal.name for signal in signals],
    }
    if metadata:
        combined_metadata.update(metadata)

    return Signal(
        samples=samples,
        sampling_rate=reference.sampling_rate,
        start_time=reference.start_time,
        name=name,
        units=reference.units,
        metadata=combined_metadata,
    )


def mix(signals: Iterable[Signal], *, name: str = "mix") -> Signal:
    """Combine an iterable of signals."""
    return composite(*tuple(signals), name=name)

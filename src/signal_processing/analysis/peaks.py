"""Robust peak detection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks

from ..core import Event, Signal
from ..utils.validation import SignalValidationError


@dataclass(slots=True)
class Peak:
    """A single detected peak."""

    index: int
    amplitude: float
    prominence: float
    left_base: int
    right_base: int
    confidence: float

    def to_event(
        self,
        sampling_rate: float,
        *,
        event_type: str = "peak",
        start_time: float = 0.0,
    ) -> Event:
        """Convert the peak into an :class:`Event` spanning its base interval."""
        left_time = start_time + self.left_base / sampling_rate
        right_time = start_time + self.right_base / sampling_rate
        peak_time = start_time + self.index / sampling_rate
        return Event(
            start_time=left_time,
            end_time=right_time,
            peak_time=peak_time,
            amplitude=self.amplitude,
            confidence=self.confidence,
            event_type=event_type,
            metadata={"peak_index": self.index},
        )


def detect_peaks(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    height: float | None = None,
    distance: int | None = None,
    prominence: float | None = None,
    threshold: float | None = None,
    minimum_confidence: float = 0.0,
) -> list[Peak]:
    """Detect peaks using SciPy's find_peaks with quality constraints."""
    if isinstance(signal, Signal):
        samples = np.asarray(signal.samples, dtype=float)
    else:
        samples = np.asarray(signal, dtype=float)

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError("Input must contain finite values.")

    if height is not None and height <= 0:
        raise SignalValidationError("height must be positive.")
    if distance is not None and int(distance) < 1:
        raise SignalValidationError("distance must be a positive integer.")
    if prominence is not None and prominence <= 0:
        raise SignalValidationError("prominence must be positive.")
    if threshold is not None and threshold <= 0:
        raise SignalValidationError("threshold must be positive.")
    if not 0.0 <= minimum_confidence <= 1.0:
        raise SignalValidationError("minimum_confidence must be in [0, 1].")

    indices, properties = find_peaks(
        samples,
        height=height,
        distance=distance,
        prominence=prominence,
        threshold=threshold,
    )

    peaks: list[Peak] = []
    for index in indices:
        amplitude = float(samples[index])
        prominences = properties.get("prominences", np.zeros(1))
        left_bases = properties.get("left_bases", np.zeros(1, dtype=int))
        right_bases = properties.get("right_bases", np.zeros(1, dtype=int))

        # Confidence combines normalized prominence with a position-aware bonus
        # so boundary candidates are weighted slightly lower.
        peak_prominence = float(prominences[0]) if prominences.size else 0.0
        scale = float(np.max(np.abs(samples))) or 1.0
        confidence = float(np.clip(np.abs(amplitude) / scale, 0.0, 1.0))
        if scale > 0 and peak_prominence > 0:
            confidence = 0.5 * confidence + 0.5 * float(
                np.clip(peak_prominence / scale, 0.0, 1.0)
            )

        peak = Peak(
            index=int(index),
            amplitude=amplitude,
            prominence=peak_prominence,
            left_base=int(left_bases[0]) if left_bases.size else int(index),
            right_base=int(right_bases[0]) if right_bases.size else int(index),
            confidence=confidence,
        )
        if confidence >= minimum_confidence:
            peaks.append(peak)

    return peaks


def peaks_to_events(
    peaks: list[Peak],
    sampling_rate: float,
    *,
    start_time: float = 0.0,
    event_type: str = "peak",
) -> list[Event]:
    """Convert :class:`Peak` objects into :class:`Event` objects."""
    return [
        peak.to_event(
            sampling_rate,
            event_type=event_type,
            start_time=start_time,
        )
        for peak in peaks
    ]

"""Event detection: thresholds, adaptive thresholds, and peaks."""

from __future__ import annotations

import numpy as np

from ..core import Event, Signal
from ..utils.validation import SignalValidationError
from .peaks import detect_peaks, peaks_to_events


def _as_1d(
    signal: Signal | np.ndarray,
    sampling_rate: float | None,
) -> tuple[np.ndarray, float, float]:
    if isinstance(signal, Signal):
        samples = np.asarray(signal.samples, dtype=float)
        rate = signal.sampling_rate
        start_time = signal.start_time
    else:
        samples = np.asarray(signal, dtype=float)
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when analyzing a plain array."
            )
        rate = float(sampling_rate)
        start_time = 0.0

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError("Input must contain finite values.")
    return samples, rate, start_time


def _build_events(
    mask: np.ndarray,
    samples: np.ndarray,
    rate: float,
    start_time: float,
    event_type: str,
    base_confidence: float,
) -> list[Event]:
    """Convert a boolean activity mask into events."""
    events: list[Event] = []
    if not np.any(mask):
        return events

    boundaries = np.flatnonzero(np.diff(np.concatenate(([0], mask.astype(int), [0]))))
    for start, stop in zip(boundaries[::2], boundaries[1::2], strict=False):
        segment = samples[start:stop]
        peak_offset = int(np.argmax(np.abs(segment)))
        peak_index = start + peak_offset

        duration_seconds = (stop - start) / rate
        confidence = float(
            np.clip(base_confidence * np.abs(samples[peak_index]) / (np.max(np.abs(samples)) or 1.0), 0.0, 1.0)
        )

        events.append(
            Event(
                start_time=start_time + start / rate,
                end_time=start_time + stop / rate,
                peak_time=start_time + peak_index / rate,
                amplitude=float(samples[peak_index]),
                confidence=confidence,
                event_type=event_type,
                metadata={"sample_start": int(start), "sample_stop": int(stop)},
            )
        )
    return events


def threshold_events(
    signal: Signal | np.ndarray,
    threshold: float,
    *,
    sampling_rate: float | None = None,
    event_type: str = "threshold",
    minimum_duration: float = 0.0,
    confidence: float = 0.8,
) -> list[Event]:
    """Detect events where |signal| exceeds an absolute threshold."""
    threshold = float(threshold)
    if not np.isfinite(threshold) or threshold <= 0:
        raise SignalValidationError("threshold must be finite and positive.")

    samples, rate, start_time = _as_1d(signal, sampling_rate)
    mask = np.abs(samples) > threshold
    events = _build_events(mask, samples, rate, start_time, event_type, confidence)

    if minimum_duration > 0:
        events = [event for event in events if event.duration >= minimum_duration]
    return events


def adaptive_threshold_events(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    window_length: int = 128,
    multiplier: float = 3.0,
    event_type: str = "adaptive_threshold",
    minimum_duration: float = 0.0,
) -> list[Event]:
    """Detect events relative to a rolling mean and standard deviation.

    The local threshold is ``rolling_mean + multiplier * rolling_std``. This
    adapts to slow amplitude drift while remaining sensitive to transients.
    """
    samples, rate, start_time = _as_1d(signal, sampling_rate)

    window_length = int(window_length)
    if window_length < 2:
        raise SignalValidationError("window_length must be at least 2.")
    multiplier = float(multiplier)
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise SignalValidationError("multiplier must be finite and positive.")

    if samples.size < window_length:
        raise SignalValidationError(
            "window_length must not exceed the number of samples."
        )

    kernel = np.ones(window_length) / window_length
    rolling_mean = np.convolve(samples, kernel, mode="same")
    centered = np.square(samples - rolling_mean)
    rolling_var = np.convolve(centered, kernel, mode="same")
    rolling_std = np.sqrt(rolling_var)

    mask = np.abs(samples - rolling_mean) > multiplier * rolling_std
    events = _build_events(mask, samples, rate, start_time, event_type, 0.9)

    if minimum_duration > 0:
        events = [event for event in events if event.duration >= minimum_duration]
    return events


def peak_events(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    height: float | None = None,
    distance: int | None = None,
    prominence: float | None = None,
    event_type: str = "peak",
) -> list[Event]:
    """Detect peaks and convert them to events."""
    if isinstance(signal, Signal):
        rate = signal.sampling_rate
        start_time = signal.start_time
    else:
        if sampling_rate is None:
            raise SignalValidationError(
                "sampling_rate is required when analyzing a plain array."
            )
        rate = float(sampling_rate)
        start_time = 0.0

    peaks = detect_peaks(
        signal,
        sampling_rate=rate,
        height=height,
        distance=distance,
        prominence=prominence,
    )
    return peaks_to_events(
        peaks,
        rate,
        start_time=start_time,
        event_type=event_type,
    )

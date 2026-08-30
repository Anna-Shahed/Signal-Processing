from __future__ import annotations

import numpy as np

from ..core import AnalysisResult, Event, Signal
from ..utils.validation import SignalValidationError


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


def _mask_to_events(
    mask: np.ndarray,
    samples: np.ndarray,
    rate: float,
    start_time: float,
    event_type: str,
) -> list[Event]:
    events: list[Event] = []
    if not np.any(mask):
        return events

    boundaries = np.flatnonzero(np.diff(np.concatenate(([0], mask.astype(int), [0]))))
    for start, stop in zip(boundaries[::2], boundaries[1::2], strict=False):
        segment = samples[start:stop]
        peak_offset = int(np.argmax(np.abs(segment)))
        peak_index = start + peak_offset
        events.append(
            Event(
                start_time=start_time + start / rate,
                end_time=start_time + stop / rate,
                peak_time=start_time + peak_index / rate,
                amplitude=float(samples[peak_index]),
                confidence=0.9,
                event_type=event_type,
                metadata={"sample_start": int(start), "sample_stop": int(stop)},
            )
        )
    return events


def zscore_anomalies(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    threshold: float = 3.0,
    window_length: int | None = None,
) -> AnalysisResult:
    """Flag samples whose z-score exceeds a threshold.

    With a window, the z-score is computed against a rolling mean and standard
    deviation; otherwise global statistics are used.
    """
    samples, rate, start_time = _as_1d(signal, sampling_rate)
    threshold = float(threshold)
    if not np.isfinite(threshold) or threshold <= 0:
        raise SignalValidationError("threshold must be finite and positive.")

    if window_length is None:
        standard_deviation = float(np.std(samples))
        if standard_deviation == 0:
            mask = np.zeros(samples.size, dtype=bool)
        else:
            z_scores = (samples - np.mean(samples)) / standard_deviation
            mask = np.abs(z_scores) > threshold
    else:
        window_length = int(window_length)
        if window_length < 2 or window_length > samples.size:
            raise SignalValidationError(
                "window_length must be between 2 and the sample count."
            )
        kernel = np.ones(window_length) / window_length
        rolling_mean = np.convolve(samples, kernel, mode="same")
        centered = np.square(samples - rolling_mean)
        rolling_var = np.convolve(centered, kernel, mode="same")
        rolling_std = np.sqrt(rolling_var)
        rolling_std[rolling_std == 0] = np.nan
        z_scores = (samples - rolling_mean) / rolling_std
        mask = np.abs(z_scores) > threshold

    return AnalysisResult(
        metrics={"n_anomalies": int(np.count_nonzero(mask))},
        arrays={
            "anomaly_mask": mask,
            "z_scores": z_scores if window_length is None else np.abs(samples - rolling_mean) / rolling_std,
        },
        metadata={"method": "zscore", "threshold": threshold},
    )


def rolling_anomalies(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    window_length: int = 128,
    multiplier: float = 3.0,
    event_type: str = "amplitude_anomaly",
) -> AnalysisResult:
    """Flag samples beyond ``multiplier`` rolling standard deviations."""
    samples, rate, start_time = _as_1d(signal, sampling_rate)

    window_length = int(window_length)
    if window_length < 2 or window_length > samples.size:
        raise SignalValidationError(
            "window_length must be between 2 and the sample count."
        )
    multiplier = float(multiplier)
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise SignalValidationError("multiplier must be finite and positive.")

    kernel = np.ones(window_length) / window_length
    rolling_mean = np.convolve(samples, kernel, mode="same")
    centered = np.square(samples - rolling_mean)
    rolling_var = np.convolve(centered, kernel, mode="same")
    rolling_std = np.sqrt(rolling_var)

    mask = np.abs(samples - rolling_mean) > multiplier * rolling_std
    events = _mask_to_events(mask, samples, rate, start_time, event_type)

    return AnalysisResult(
        metrics={"n_anomalies": len(events)},
        arrays={
            "anomaly_mask": mask,
            "rolling_mean": rolling_mean,
            "rolling_std": rolling_std,
        },
        metadata={"method": "rolling", "window_length": window_length, "multiplier": multiplier},
    )


def robust_threshold_anomalies(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    multiplier: float = 3.0,
) -> AnalysisResult:
    """Flag samples beyond a robust MAD-based threshold."""
    samples, rate, start_time = _as_1d(signal, sampling_rate)
    multiplier = float(multiplier)
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise SignalValidationError("multiplier must be finite and positive.")

    median_value = float(np.median(samples))
    mad = float(np.median(np.abs(samples - median_value)))
    if mad == 0:
        mask = np.zeros(samples.size, dtype=bool)
    else:
        robust_std = 1.4826 * mad
        mask = np.abs(samples - median_value) > multiplier * robust_std

    events = _mask_to_events(mask, samples, rate, start_time, "robust_anomaly")
    return AnalysisResult(
        metrics={"n_anomalies": len(events)},
        arrays={"anomaly_mask": mask},
        metadata={"method": "robust_mad", "multiplier": multiplier},
    )


def energy_anomalies(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    frame_length: int = 128,
    hop_length: int | None = None,
    multiplier: float = 3.0,
) -> AnalysisResult:
    """Flag frames whose RMS energy exceeds a robust threshold."""
    samples, rate, start_time = _as_1d(signal, sampling_rate)
    frame_length = int(frame_length)
    if frame_length < 2 or frame_length > samples.size:
        raise SignalValidationError(
            "frame_length must be between 2 and the sample count."
        )
    hop = frame_length // 2 if hop_length is None else int(hop_length)
    if hop < 1:
        raise SignalValidationError("hop_length must be positive.")
    multiplier = float(multiplier)
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise SignalValidationError("multiplier must be finite and positive.")

    frame_energies: list[float] = []
    frame_times: list[float] = []
    for start in range(0, samples.size - frame_length + 1, hop):
        frame = samples[start : start + frame_length]
        frame_energies.append(float(np.sqrt(np.mean(np.square(frame)))))
        frame_times.append(start_time + (start + frame_length / 2) / rate)

    energies = np.asarray(frame_energies)
    median_energy = float(np.median(energies))
    mad = float(np.median(np.abs(energies - median_energy)))
    if mad == 0:
        mask = np.zeros(energies.size, dtype=bool)
    else:
        mask = energies > median_energy + multiplier * 1.4826 * mad

    flagged_times = np.asarray(frame_times)[mask]
    events = [
        Event(
            start_time=max(start_time, float(t - frame_length / (2 * rate))),
            end_time=min(start_time + samples.size / rate, float(t + frame_length / (2 * rate))),
            peak_time=float(t),
            amplitude=float(energies[index]),
            confidence=0.85,
            event_type="energy_anomaly",
            metadata={"frame_index": int(index)},
        )
        for index, t in enumerate(np.asarray(frame_times))
        if mask[index]
    ]

    return AnalysisResult(
        metrics={"n_anomalies": len(events)},
        arrays={"frame_energies": energies, "frame_times": np.asarray(frame_times)},
        metadata={"method": "energy", "multiplier": multiplier},
    )


def detect_anomalies(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    method: str = "zscore",
    threshold: float = 3.0,
    window_length: int | None = None,
    multiplier: float = 3.0,
    frame_length: int = 128,
    hop_length: int | None = None,
    event_type: str = "amplitude_anomaly",
) -> AnalysisResult:
   
    name = str(method).lower().strip()
    if name == "zscore":
        return zscore_anomalies(
            signal, sampling_rate=sampling_rate,
            threshold=threshold, window_length=window_length,
        )
    if name == "rolling":
        return rolling_anomalies(
            signal, sampling_rate=sampling_rate,
            window_length=window_length if window_length is not None else 128,
            multiplier=multiplier, event_type=event_type,
        )
    if name == "robust":
        return robust_threshold_anomalies(
            signal, sampling_rate=sampling_rate, multiplier=multiplier,
        )
    if name == "energy":
        return energy_anomalies(
            signal, sampling_rate=sampling_rate,
            frame_length=frame_length, hop_length=hop_length, multiplier=multiplier,
        )
    raise SignalValidationError(
        f"Unknown anomaly method: {method!r}. Choose from "
        f"{['zscore', 'rolling', 'robust', 'energy']}."
    )

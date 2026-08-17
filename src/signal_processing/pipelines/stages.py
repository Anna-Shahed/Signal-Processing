"""Composable pipeline stage primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

import numpy as np

from ..core import AnalysisResult, Signal


class Stage(Protocol):
    """A pipeline stage transforms a signal and/or produces a result."""

    name: str

    def apply(self, signal: Signal) -> Signal | AnalysisResult: ...


@dataclass(slots=True)
class FunctionStage:
    """Wrap an arbitrary callable as a named pipeline stage."""

    function: Callable[[Signal], Signal | AnalysisResult]
    name: str

    def apply(self, signal: Signal) -> Signal | AnalysisResult:
        return self.function(signal)


def _detrend(signal: Signal) -> Signal:
    from scipy.signal import detrend as scipy_detrend

    return signal.copy(
        samples=scipy_detrend(signal.samples, axis=0),
        metadata={**signal.metadata, "pipeline_stage": "detrend"},
    )


def _normalize(signal: Signal) -> Signal:
    return signal.normalize(mode="peak", target=1.0)


def detrend() -> FunctionStage:
    """Remove the best-fit linear trend from the signal."""
    return FunctionStage(_detrend, "detrend")


def normalize() -> FunctionStage:
    """Normalize the signal to unit peak amplitude."""
    return FunctionStage(_normalize, "normalize")


def lowpass(cutoff: float, order: int = 5) -> FunctionStage:
    """Apply a zero-phase Butterworth low-pass filter stage."""
    from ..filters.iir import butterworth_lowpass, iir_filter

    def stage(signal: Signal) -> Signal:
        coefficients = butterworth_lowpass(order, cutoff, signal.sampling_rate)
        return iir_filter(signal, coefficients, zero_phase=True, name="lowpassed")

    return FunctionStage(stage, f"lowpass_{cutoff}hz")


def highpass(cutoff: float, order: int = 5) -> FunctionStage:
    """Apply a zero-phase Butterworth high-pass filter stage."""
    from ..filters.iir import butterworth_highpass, iir_filter

    def stage(signal: Signal) -> Signal:
        coefficients = butterworth_highpass(order, cutoff, signal.sampling_rate)
        return iir_filter(signal, coefficients, zero_phase=True, name="highpassed")

    return FunctionStage(stage, f"highpass_{cutoff}hz")


def fft_stage(one_sided: bool = True) -> FunctionStage:
    """Compute an FFT and return its spectrum as an AnalysisResult."""
    from ..transforms.fft import fft

    def stage(signal: Signal) -> AnalysisResult:
        spectrum = fft(signal, one_sided=one_sided)
        return AnalysisResult(
            metrics={
                "dominant_frequency": spectrum.dominant_frequency,
                "peak_magnitude": float(np.max(spectrum.magnitude)),
            },
            arrays={
                "frequencies": spectrum.frequencies,
                "values": spectrum.values,
            },
            metadata={"stage": "fft"},
        )

    return FunctionStage(stage, "fft")


def peak_detection(
    height: float | None = None,
    distance: int | None = None,
    prominence: float | None = None,
) -> FunctionStage:
    """Detect peaks and return them as events inside an AnalysisResult."""
    from ..analysis.peaks import detect_peaks, peaks_to_events

    def stage(signal: Signal) -> AnalysisResult:
        peaks = detect_peaks(
            signal,
            height=height,
            distance=distance,
            prominence=prominence,
        )
        events = peaks_to_events(
            peaks,
            signal.sampling_rate,
            start_time=signal.start_time,
        )
        return AnalysisResult(
            metrics={"n_peaks": len(events)},
            arrays={
                "peak_indices": np.asarray(
                    [event.metadata.get("peak_index", -1) for event in events],
                    dtype=int,
                )
            },
            metadata={"stage": "peak_detection"},
        )

    return FunctionStage(stage, "peak_detection")

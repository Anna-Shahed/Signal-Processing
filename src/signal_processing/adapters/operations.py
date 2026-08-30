from __future__ import annotations

from typing import Any

import numpy as np

from ..analysis import analyze, detect_peaks
from ..analysis.anomaly import detect_anomalies
from ..analysis.events import detect_events
from ..analysis.kalman import KalmanFilter
from ..core import Signal
from ..filters import (
    design_bandpass,
    design_bandstop,
    design_butterworth,
    design_highpass,
    design_lowpass,
    fir_filter,
    iir_filter,
)
from ..generators import (
    chirp,
    composite,
    cosine,
    gaussian_noise,
    sawtooth,
    sine,
    square,
    triangle,
    white_noise,
)
from ..operations import convolve, cross_correlation, resample
from ..pipelines import Pipeline, detrend, fft_stage, highpass, lowpass, normalize
from ..transforms.fft import fft, frequency_bins
from ..transforms.stft import stft

_WAVEFORMS = {
    "sine": sine, "cosine": cosine, "square": square, "triangle": triangle,
    "sawtooth": sawtooth, "chirp": chirp,
}


def _arr(a: Any) -> list[float]:
    return np.asarray(a, dtype=float).tolist()


def _signal_to_dict(s: Signal) -> dict:
    return {
        "samples": _arr(s.samples),
        "sampling_rate": float(s.sampling_rate),
        "duration": float(s.duration),
        "name": s.name,
        "units": s.units,
    }


def _ok(**kw: Any) -> dict:
    return {"status": "ok", **kw}

def generate_signal(
    waveform: str,
    frequency: float = 440.0,
    duration: float = 1.0,
    sampling_rate: float = 8_000,
    amplitude: float = 1.0,
    phase: float = 0.0,
    duty: float = 0.5,
    frequency_end: float | None = None,
    seed: int | None = None,
    noise_amplitude: float = 0.0,
) -> dict:
    """Generate a synthetic waveform: sine, cosine, square, triangle, sawtooth,
    chirp, white_noise, gaussian_noise, or composite (noise added to tone)."""
    name = waveform
    if waveform in _WAVEFORMS:
        fn = _WAVEFORMS[waveform]
        if waveform == "square":
            sig = fn(frequency, amplitude, duration, sampling_rate, duty=duty,
                     name=name, units="V")
        elif waveform == "chirp":
            f1 = frequency_end if frequency_end is not None else 2 * frequency
            sig = fn(frequency, f1, duration, sampling_rate, name=name, units="V")
        else:
            sig = fn(frequency, amplitude, phase, duration, sampling_rate,
                     name=name, units="V")
    elif waveform == "white_noise":
        sig = white_noise(duration, sampling_rate, amplitude=amplitude, seed=seed,
                          name=name, units="V")
    elif waveform == "gaussian_noise":
        sig = gaussian_noise(duration, sampling_rate, amplitude=amplitude, seed=seed,
                             name=name, units="V")
    else:
        raise ValueError(f"Unknown waveform: {waveform}")
    if noise_amplitude > 0:
        noise = white_noise(duration, sampling_rate, amplitude=noise_amplitude,
                            seed=seed, name="noise", units="V")
        sig = composite(sig, noise, name=name)
    return _ok(signal=_signal_to_dict(sig))


def fft_spectrum(
    samples: list[float],
    sampling_rate: float,
    one_sided: bool = True,
    n: int | None = None,
) -> dict:
    """Compute the (optionally one-sided) magnitude spectrum of a signal."""
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    spec = fft(sig, one_sided=one_sided, n=n)
    freqs = spec.frequencies if hasattr(spec, "frequencies") else frequency_bins(
        spec.values.size, sampling_rate, one_sided=one_sided)
    return _ok(frequencies=_arr(freqs), magnitudes=_arr(np.abs(spec.values)))


def filter_signal(
    samples: list[float],
    sampling_rate: float,
    kind: str = "fir",
    filter_type: str = "lowpass",
    cutoff: float = 1_000.0,
    cutoff_high: float | None = None,
    order: int = 64,
    zero_phase: bool = True,
) -> dict:
    """Apply a FIR or Butterworth IIR filter (lowpass/highpass/bandpass/bandstop)."""
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    if kind == "fir":
        if filter_type == "lowpass":
            b = design_lowpass(order, cutoff, sampling_rate)
        elif filter_type == "highpass":
            b = design_highpass(order, cutoff, sampling_rate)
        elif filter_type == "bandpass":
            b = design_bandpass(order, cutoff, cutoff_high or cutoff * 2, sampling_rate)
        else:
            b = design_bandstop(order, cutoff, cutoff_high or cutoff * 2, sampling_rate)
        out = fir_filter(sig, b, zero_phase=zero_phase)
    else:
        btype = {"lowpass": "lowpass", "highpass": "highpass",
                 "bandpass": "bandpass", "bandstop": "bandstop"}[filter_type]
        cutoff_vals = [cutoff] if cutoff_high is None else [cutoff, cutoff_high]
        b, a = design_butterworth(btype, cutoff_vals, sampling_rate, order=max(2, order // 8))
        out = iir_filter(sig, b, a, zero_phase=zero_phase)
    return _ok(signal=_signal_to_dict(out))


def analyze_signal(samples: list[float], sampling_rate: float) -> dict:
    """Return the full statistical/spectral metric set (mean, rms, SNR, dominant frequency, ...)."""
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    result = analyze(sig)
    return _ok(metrics={k: (float(v) if isinstance(v, (int, float, np.floating))
                            else v) for k, v in result.metrics.items()})


def detect_events_op(
    samples: list[float],
    sampling_rate: float,
    method: str = "threshold",
    threshold: float = 0.5,
) -> dict:
    """Detect events (threshold, adaptive, or peak based) and return intervals."""
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    events = detect_events(sig, method=method, threshold=threshold)
    return _ok(events=[{"start": float(e.start), "end": float(e.end),
                        "label": getattr(e, "label", None),
                        "confidence": float(getattr(e, "confidence", 1.0))}
                       for e in events])


def detect_anomalies_op(
    samples: list[float],
    method: str = "zscore",
    threshold: float = 3.0,
) -> dict:
    """Detect anomalies (zscore, rolling, robust, amplitude, energy)."""
    anomalies = detect_anomalies(np.asarray(samples, dtype=float),
                                 method=method, threshold=threshold)
    return _ok(anomalies=_arr(anomalies))


def stft_op(
    samples: list[float],
    sampling_rate: float,
    window_length: int = 256,
    hop_length: int | None = None,
    window: str = "hann",
) -> dict:
    """Short-time Fourier transform: times, frequencies, and magnitude matrix."""
    hop = hop_length or window_length // 2
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    res = stft(sig, window_length=window_length, hop_length=hop, window=window)
    return _ok(
        times=_arr(res.times),
        frequencies=_arr(res.frequencies),
        magnitudes=[[float(v) for v in row] for row in np.abs(res.values)],
    )


def resample_op(samples: list[float], sampling_rate: float,
                target_rate: float) -> dict:
    """Rational resampling with anti-aliasing to a new sampling rate."""
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    out = resample(sig, target_rate)
    return _ok(signal=_signal_to_dict(out))


def convolve_op(a: list[float], b: list[float], mode: str = "same") -> dict:

    result = convolve(np.asarray(a, dtype=float), np.asarray(b, dtype=float), mode=mode)
    return _ok(result=_arr(result))


def kalman_op(
    samples: list[float],
    process_variance: float = 1e-4,
    measurement_variance: float = 1e-2,
) -> dict:
   
    kf = KalmanFilter(process_variance, measurement_variance)
    out = kf.filter(np.asarray(samples, dtype=float))
    filtered = out.filtered if hasattr(out, "filtered") else out.samples
    return _ok(filtered=_arr(filtered))


def pipeline_run(
    samples: list[float],
    sampling_rate: float,
    stages: list[str],
    cutoff: float = 100.0,
    order: int = 4,
) -> dict:
    
    sig = Signal(np.asarray(samples, dtype=float), sampling_rate=sampling_rate)
    pipe = Pipeline()
    for stage in stages:
        if stage == "detrend":
            pipe.add(detrend())
        elif stage == "normalize":
            pipe.add(normalize())
        elif stage == "lowpass":
            pipe.add(lowpass(cutoff=cutoff, order=order))
        elif stage == "highpass":
            pipe.add(highpass(cutoff=cutoff, order=order))
        elif stage == "fft":
            pipe.add(fft_stage(one_sided=True))
        else:
            raise ValueError(f"Unknown pipeline stage: {stage}")
    final = pipe.run(sig)
    return _ok(
        signal=_signal_to_dict(final) if hasattr(final, "sampling_rate") else None,
        metrics={k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                 for k, v in final.metrics.items()} if hasattr(final, "metrics") else {},
    )

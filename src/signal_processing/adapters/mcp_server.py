from __future__ import annotations

from typing import Any

try:
    from mcp.server import MCPServer as _Server  # mcp SDK >= 2  ← adjust if your version differs
    _HAS_V2 = True
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP as _Server  # mcp SDK 1.x
    _HAS_V2 = False

from .adapters.operations import (
    analyze_signal,
    convolve_op,
    detect_anomalies_op,
    detect_events_op,
    fft_spectrum,
    filter_signal as _filter_signal,
    generate_signal,
    kalman_op,
    pipeline_run,
    resample_op,
    stft_op,
)

mcp = _Server("signal-lab")


@mcp.tool()
def generate(waveform: str, frequency: float = 440.0, duration: float = 1.0,
             sampling_rate: float = 8_000, amplitude: float = 1.0,
             phase: float = 0.0, duty: float = 0.5, frequency_end: float | None = None,
             seed: int | None = None, noise_amplitude: float = 0.0) -> dict:
    """Generate a synthetic waveform (sine, cosine, square, triangle, sawtooth,
    chirp, white_noise, gaussian_noise). Returns samples + sampling_rate."""
    return generate_signal(waveform, frequency, duration, sampling_rate,
                           amplitude, phase, duty, frequency_end, seed, noise_amplitude)


@mcp.tool()
def spectrum(samples: list[float], sampling_rate: float, one_sided: bool = True) -> dict:
    """Compute the magnitude spectrum (frequencies + magnitudes)."""
    return fft_spectrum(samples, sampling_rate, one_sided=one_sided)


@mcp.tool()
def filter_signal(samples: list[float], sampling_rate: float, kind: str = "fir",
                 filter_type: str = "lowpass", cutoff: float = 1_000.0,
                 cutoff_high: float | None = None, order: int = 64,
                 zero_phase: bool = True) -> dict:
    """Apply a FIR or Butterworth IIR filter (lowpass/highpass/bandpass/bandstop)."""
    return _filter_signal(samples, sampling_rate, kind, filter_type, cutoff,
                          cutoff_high, order, zero_phase)


@mcp.tool()
def analyze(samples: list[float], sampling_rate: float) -> dict:
    """Return full metrics: mean, rms, peak, crest, SNR, dominant frequency, etc."""
    return analyze_signal(samples, sampling_rate)


@mcp.tool()
def detect_events(samples: list[float], sampling_rate: float, method: str = "threshold",
                  threshold: float = 0.5) -> dict:
    """Detect events (threshold, adaptive, peak) and return intervals."""
    return detect_events_op(samples, sampling_rate, method, threshold)


@mcp.tool()
def detect_anomalies(samples: list[float], method: str = "zscore",
                     threshold: float = 3.0) -> dict:
    """Detect anomalies (zscore, rolling, robust, amplitude, energy)."""
    return detect_anomalies_op(samples, method, threshold)


@mcp.tool()
def spectrogram(samples: list[float], sampling_rate: float, window_length: int = 256) -> dict:
    """Short-time Fourier transform: times, frequencies, magnitude matrix."""
    return stft_op(samples, sampling_rate, window_length=window_length)


@mcp.tool()
def resample(samples: list[float], sampling_rate: float, target_rate: float) -> dict:
    """Resample a signal to a new sampling rate with anti-aliasing."""
    return resample_op(samples, sampling_rate, target_rate)


@mcp.tool()
def convolve(a: list[float], b: list[float], mode: str = "same") -> dict:
    """Linear convolution of two signals."""
    return convolve_op(a, b, mode)


@mcp.tool()
def kalman(samples: list[float], process_variance: float = 1e-4,
           measurement_variance: float = 1e-2) -> dict:
    """Kalman-filter a noisy measurement series."""
    return kalman_op(samples, process_variance, measurement_variance)


@mcp.tool()
def pipeline(samples: list[float], sampling_rate: float, stages: list[str],
             cutoff: float = 100.0, order: int = 4) -> dict:
    """Run a named pipeline (detrend, normalize, lowpass, highpass, fft)."""
    return pipeline_run(samples, sampling_rate, stages, cutoff, order)


def mcp_asgi():
    """ASGI app for streamable-http transport (mounted by FastAPI at /mcp)."""
    for attr in ("streamable_http_app", "sse_app"):
        fn = getattr(mcp, attr, None)
        if fn is not None:
            return fn()
    raise RuntimeError("This mcp SDK version exposes no HTTP app helper.")


def main() -> None:
    mcp.run()  # stdio by default; pass transport="streamable-http" for remote


if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import Any

try:
    from mcp.server import MCPServer as _Server  
    _HAS_V2 = True
except ImportError:  
    from mcp.server.fastmcp import FastMCP as _Server  
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
  
    return generate_signal(waveform, frequency, duration, sampling_rate,
                           amplitude, phase, duty, frequency_end, seed, noise_amplitude)

@mcp.tool()
def spectrum(samples: list[float], sampling_rate: float, one_sided: bool = True) -> dict:
    return fft_spectrum(samples, sampling_rate, one_sided=one_sided)


@mcp.tool()
def filter_signal(samples: list[float], sampling_rate: float, kind: str = "fir",
                 filter_type: str = "lowpass", cutoff: float = 1_000.0,
                 cutoff_high: float | None = None, order: int = 64,
                 zero_phase: bool = True) -> dict:
    return _filter_signal(samples, sampling_rate, kind, filter_type, cutoff,
                          cutoff_high, order, zero_phase)


@mcp.tool()
def analyze(samples: list[float], sampling_rate: float) -> dict:
    return analyze_signal(samples, sampling_rate)


@mcp.tool()
def detect_events(samples: list[float], sampling_rate: float, method: str = "threshold",
                  threshold: float = 0.5) -> dict:
    return detect_events_op(samples, sampling_rate, method, threshold)


@mcp.tool()
def detect_anomalies(samples: list[float], method: str = "zscore",
                     threshold: float = 3.0) -> dict:
    return detect_anomalies_op(samples, method, threshold)


@mcp.tool()
def spectrogram(samples: list[float], sampling_rate: float, window_length: int = 256) -> dict:
    return stft_op(samples, sampling_rate, window_length=window_length)


@mcp.tool()
def resample(samples: list[float], sampling_rate: float, target_rate: float) -> dict:
    return resample_op(samples, sampling_rate, target_rate)


@mcp.tool()
def convolve(a: list[float], b: list[float], mode: str = "same") -> dict:
    return convolve_op(a, b, mode)


@mcp.tool()
def kalman(samples: list[float], process_variance: float = 1e-4,
           measurement_variance: float = 1e-2) -> dict:
    return kalman_op(samples, process_variance, measurement_variance)


@mcp.tool()
def pipeline(samples: list[float], sampling_rate: float, stages: list[str],
             cutoff: float = 100.0, order: int = 4) -> dict:
    return pipeline_run(samples, sampling_rate, stages, cutoff, order)


def mcp_asgi():
    for attr in ("streamable_http_app", "sse_app"):
        fn = getattr(mcp, attr, None)
        if fn is not None:
            return fn()
    raise RuntimeError("This mcp SDK version exposes no HTTP app helper.")


def main() -> None:
    mcp.run()  

if __name__ == "__main__":
    main()

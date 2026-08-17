"""Command-line interface for the Signal Processing Laboratory.

Entry point: ``signal-process`` (declared in ``pyproject.toml`` under
``[project.scripts]``). The CLI mirrors the library's public API so that
every interactive capability is also scriptable:

    signal-process generate --waveform sine --frequency 440 --duration 2 -o tone.wav
    signal-process fft tone.wav --peaks 5
    signal-process filter tone.wav --kind fir --type lowpass --cutoff 1000 --order 101
    signal-process spectrogram tone.wav -o spectrogram.png
    signal-process analyze tone.wav
    signal-process detect tone.wav --method threshold --threshold 0.5
    signal-process convert tone.wav --format csv -o tone.csv
    signal-process demo
    signal-process lab
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

from .. import __version__
from ..analysis import analyze
from ..analysis.events import detect_events
from ..core import Signal, SignalIOError
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
from ..io import read_csv, read_wav, write_csv, write_json, write_wav
from ..io.json import signal_from_json, to_json_string
from ..transforms.fft import fft
from ..transforms.stft import stft
from ..visualization.dashboard import plot_dashboard, plot_filter_response
from ..visualization.spectrogram_plot import plot_spectrogram
from ..visualization.spectrum_plot import plot_spectrum


def load_signal(path: str | Path) -> Signal:
    """Load a signal from WAV, CSV, or JSON (format chosen by extension)."""
    p = Path(path)
    suffix = p.suffix.lower()
    try:
        if suffix in {".wav", ".flac", ".ogg", ".opus"}:
            return read_wav(p)
        if suffix == ".csv":
            return read_csv(p)
        if suffix == ".json":
            return signal_from_json(p)
    except Exception as exc:  # noqa: BLE001 - wrap foreign exceptions
        raise SignalIOError(f"Failed to load {p}: {exc}") from exc
    raise SignalIOError(f"Unsupported input format: {suffix or '(none)'}")


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_generate(args: argparse.Namespace) -> int:
    kwargs = {"name": args.waveform, "units": "V"}
    if args.waveform == "sine":
        base = sine(args.frequency, args.amplitude, args.phase, args.duration, args.sampling_rate, **kwargs)
    elif args.waveform == "cosine":
        base = cosine(args.frequency, args.amplitude, args.phase, args.duration, args.sampling_rate, **kwargs)
    elif args.waveform == "square":
        base = square(args.frequency, args.amplitude, args.duration, args.sampling_rate, **kwargs)
    elif args.waveform == "triangle":
        base = triangle(args.frequency, args.amplitude, args.duration, args.sampling_rate, **kwargs)
    elif args.waveform == "sawtooth":
        base = sawtooth(args.frequency, args.amplitude, args.duration, args.sampling_rate, **kwargs)
    elif args.waveform == "chirp":
        base = chirp(args.frequency, args.end_frequency, args.duration, args.sampling_rate,
                     kind=args.chirp_kind, amplitude=args.amplitude, phase=args.phase, **kwargs)
    elif args.waveform == "white-noise":
        base = white_noise(args.duration, args.sampling_rate, amplitude=args.amplitude,
                           seed=args.seed, **kwargs)
    else:  # gaussian-noise
        base = gaussian_noise(args.duration, args.sampling_rate, amplitude=args.amplitude,
                              seed=args.seed, **kwargs)

    signal = base
    if args.noise_amplitude > 0:
        noise = white_noise(args.duration, args.sampling_rate,
                            amplitude=args.noise_amplitude, seed=args.seed)
        signal = composite(base, noise)

    out = Path(args.output)
    if out.suffix.lower() in {".csv"}:
        write_csv(signal, out)
    else:
        write_wav(signal, out)
    print(f"Generated {args.waveform} -> {out} "
          f"({signal.n_samples} samples, fs={signal.sampling_rate:g} Hz, "
          f"duration={signal.duration:.3f} s)")
    return 0


def cmd_fft(args: argparse.Namespace) -> int:
    from scipy.signal import find_peaks

    signal = load_signal(args.input)
    spec = fft(signal, one_sided=True)
    freqs = np.asarray(spec.frequencies)
    mag = np.abs(np.asarray(spec.values))

    peaks, props = find_peaks(mag, height=mag.max() * 1e-4)
    order = np.argsort(props["peak_heights"])[::-1][: args.peaks]

    print(f"FFT of {args.input} ({signal.n_samples} samples, fs={signal.sampling_rate:g} Hz)")
    print(f"Dominant frequency : {spec.dominant_frequency:9.3f} Hz")
    print(f"Spectral centroid : {spec.spectral_centroid:9.3f} Hz")
    print(f"Top {len(order)} peaks:")
    print("  #     freq (Hz)      |X|        dB")
    for i, idx in enumerate(order):
        f = freqs[peaks[idx]]
        m = mag[peaks[idx]]
        db = 20.0 * np.log10(max(m, 1e-12))
        print(f"  {i + 1:2d}  {f:12.3f}  {m:12.6g}  {db:8.3f}")

    if args.output:
        fig, _ = plot_spectrum(spec, db=True, title=f"FFT — {Path(args.input).name}")
        fig.savefig(args.output, dpi=160)
        print(f"Saved figure -> {args.output}")
    if args.json:
        write_json({"dominant_frequency": float(spec.dominant_frequency),
                    "spectral_centroid": float(spec.spectral_centroid),
                    "peaks": [{"frequency": float(freqs[peaks[idx]]),
                               "magnitude": float(mag[peaks[idx]])} for idx in order]},
                   args.json)
        print(f"Saved JSON -> {args.json}")
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    signal = load_signal(args.input)
    fs = signal.sampling_rate
    a = [1.0]

    if args.kind == "fir":
        numtaps = args.order + 1 if args.order % 2 == 0 else args.order
        if args.type == "lowpass":
            b = design_lowpass(numtaps, args.cutoff, fs, window=args.window)
        elif args.type == "highpass":
            b = design_highpass(numtaps, args.cutoff, fs, window=args.window)
        elif args.type == "bandpass":
            b = design_bandpass(numtaps, args.cutoff_low, args.cutoff_high, fs, window=args.window)
        else:
            b = design_bandstop(numtaps, args.cutoff_low, args.cutoff_high, fs, window=args.window)
        filtered = fir_filter(signal, b, zero_phase=not args.causal)
        description = f"FIR {args.type} ({numtaps} taps, {args.window})"
    else:
        cutoff = args.cutoff if args.type in {"lowpass", "highpass"} else (args.cutoff_low, args.cutoff_high)
        b, a = design_butterworth(args.type, cutoff, fs, order=args.order)
        filtered = iir_filter(signal, b, a, zero_phase=not args.causal)
        description = f"Butterworth {args.type} (order {args.order})"

    write_wav(filtered, args.output)
    print(f"Applied {description} -> {args.output}")
    print(f"  before: peak={np.max(np.abs(signal.samples)):.6g}  "
          f"rms={np.sqrt(np.mean(signal.samples ** 2)):.6g}")
    print(f"  after : peak={np.max(np.abs(filtered.samples)):.6g}  "
          f"rms={np.sqrt(np.mean(filtered.samples ** 2)):.6g}")

    if args.response:
        fig, _ = plot_filter_response(b, a, sampling_rate=fs, title=description)
        fig.savefig(args.response, dpi=160)
        print(f"Saved response -> {args.response}")
    return 0


def cmd_spectrogram(args: argparse.Namespace) -> int:
    signal = load_signal(args.input)
    spec = stft(signal, nperseg=args.nperseg, hop_length=args.hop, window=args.window)
    print(f"STFT of {args.input}: {spec.times.size} frames x {spec.frequencies.size} bins")
    print(f"  resolution: df={spec.frequencies[1] - spec.frequencies[0]:.3f} Hz, "
          f"dt={spec.times[1] - spec.times[0]:.5f} s")
    if args.output:
        fig, _ = plot_spectrogram(spec, db=True, title=f"Spectrogram — {Path(args.input).name}")
        fig.savefig(args.output, dpi=160)
        print(f"Saved figure -> {args.output}")
    if args.json:
        write_json({"times": spec.times, "frequencies": spec.frequencies,
                    "magnitude_db": 20.0 * np.log10(np.maximum(np.abs(spec.values), 1e-8))},
                   args.json)
        print(f"Saved JSON -> {args.json}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    signal = load_signal(args.input)
    result = analyze(signal)
    print(result.summary())
    if args.json:
        write_json(result, args.json)
        print(f"Saved JSON -> {args.json}")
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    signal = load_signal(args.input)
    events = detect_events(
        signal,
        method=args.method,
        threshold=args.threshold,
        rms_multiplier=args.rms_multiplier,
        min_distance=args.min_distance,
        prominence=args.prominence,
    )
    print(f"Detected {len(events)} event(s) with method '{args.method}':")
    print("  start (s)   end (s)    peak (s)   amplitude  duration (s)  confidence")
    for e in events:
        print(f"  {e.start_time:9.4f}  {e.end_time:9.4f}  {e.peak_time:9.4f}  "
              f"{e.amplitude:9.4f}  {e.duration:9.4f}  {e.confidence:6.3f}")
    if args.output:
        from ..visualization.signal_plot import plot_signal
        fig, _ = plot_signal(signal, events=events, title=f"Events — {Path(args.input).name}")
        fig.savefig(args.output, dpi=160)
        print(f"Saved figure -> {args.output}")
    if args.json:
        write_json([e.to_dict() for e in events], args.json)
        print(f"Saved JSON -> {args.json}")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    signal = load_signal(args.input)
    out = Path(args.output)
    fmt = args.format or out.suffix.lower().lstrip(".")
    if fmt == "wav":
        write_wav(signal, out)
    elif fmt == "csv":
        write_csv(signal, out)
    elif fmt == "json":
        write_json(signal, out)
    else:
        raise SignalIOError(f"Unsupported conversion format: {fmt}")
    print(f"Converted {args.input} -> {out}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Run the canonical end-to-end pipeline and write artifacts to a folder."""
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    tone = sine(50, amplitude=1.0, duration=2.0

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
from ..io.json import signal_from_json
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


def cmd_generate(args: argparse.Namespace) -> int:
    kwargs = {"name": args.waveform, "units": "V"}
    if args.waveform == "sine":
        base = sine(args.frequency, args.amplitude, args.phase, args.duration,
                    args.sampling_rate, **kwargs)
    elif args.waveform == "cosine":
        base = cosine(args.frequency, args.amplitude, args.phase, args.duration,
                      args.sampling_rate, **kwargs)
    elif args.waveform == "square":
        base = square(args.frequency, args.amplitude, args.duration,
                      args.sampling_rate, **kwargs)
    elif args.waveform == "triangle":
        base = triangle(args.frequency, args.amplitude, args.duration,
                        args.sampling_rate, **kwargs)
    elif args.waveform == "sawtooth":
        base = sawtooth(args.frequency, args.amplitude, args.duration,
                        args.sampling_rate, **kwargs)
    elif args.waveform == "chirp":
        base = chirp(args.frequency, args.end_frequency, args.duration,
                     args.sampling_rate, kind=args.chirp_kind,
                     amplitude=args.amplitude, phase=args.phase, **kwargs)
    elif args.waveform == "white-noise":
        base = white_noise(args.duration, args.sampling_rate,
                           amplitude=args.amplitude, seed=args.seed, **kwargs)
    else:  # gaussian-noise
        base = gaussian_noise(args.duration, args.sampling_rate,
                              amplitude=args.amplitude, seed=args.seed, **kwargs)

    signal = base
    if args.noise_amplitude > 0:
        signal = composite(base, white_noise(args.duration, args.sampling_rate,
                                             amplitude=args.noise_amplitude,
                                             seed=args.seed))

    out = Path(args.output)
    if out.suffix.lower() == ".csv":
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
        write_json(
            {
                "dominant_frequency": float(spec.dominant_frequency),
                "spectral_centroid": float(spec.spectral_centroid),
                "peaks": [
                    {"frequency": float(freqs[peaks[idx]]),
                     "magnitude": float(mag[peaks[idx]])}
                    for idx in order
                ],
            },
            args.json,
        )
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
        cutoff = args.cutoff if args.type in {"lowpass", "highpass"} \
            else (args.cutoff_low, args.cutoff_high)
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
        write_json(
            {
                "times": spec.times,
                "frequencies": spec.frequencies,
                "magnitude_db": 20.0 * np.log10(
                    np.maximum(np.abs(spec.values), 1e-8)
                ),
            },
            args.json,
        )
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

        fig, _ = plot_signal(signal, events=events,
                             title=f"Events — {Path(args.input).name}")
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

    tone = sine(50, amplitude=1.0, duration=2.0, sampling_rate=2_000)
    noise = white_noise(2.0, 2_000, amplitude=0.15, seed=7)
    raw = composite(tone, noise)
    write_wav(raw, out / "01_raw.wav")

    b = design_lowpass(101, 150, 2_000, window="hamming")
    cleaned = fir_filter(raw, b, zero_phase=True)
    write_wav(cleaned, out / "02_filtered.wav")

    spec = fft(cleaned, one_sided=True)
    specgram = stft(cleaned, nperseg=256, hop_length=128, window="hann")
    result = analyze(cleaned)
    events = detect_events(cleaned, method="threshold", threshold=0.5)

    write_json(result, out / "03_analysis.json")
    write_json([e.to_dict() for e in events], out / "04_events.json")

    fig, _ = plot_dashboard(
        cleaned,
        spectrum=spec,
        spectrogram=specgram,
        events=events,
        title="Signal Processing Laboratory — demo",
    )
    fig.savefig(out / "05_dashboard.png", dpi=160)

    print(f"Demo artifacts written to {out.resolve()}:")
    for p in sorted(out.iterdir()):
        print(f"  - {p.name} ({p.stat().st_size} bytes)")
    print(f"Dominant frequency: {result.metrics.get('dominant_frequency', float('nan')):.3f} Hz")
    print(f"Detected events   : {len(events)}")
    return 0


def cmd_lab(args: argparse.Namespace) -> int:
    """Launch the Streamlit laboratory."""
    candidates = [
        Path(os.environ.get("SIGNAL_PROCESSING_APP", "")),
        Path(__file__).resolve().parents[3] / "app" / "main.py",
        Path.cwd() / "app" / "main.py",
    ]
    app_path = next((p for p in candidates if str(p) and p.is_file()), None)
    if app_path is None:
        print("Could not locate app/main.py. "
              "Run `streamlit run app/main.py` from the repository root.")
        return 1
    print(f"Launching laboratory: {app_path}")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    if args.port:
        cmd += ["--server.port", str(args.port)]
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="signal-process",
        description="Signal Processing Laboratory — command-line laboratory.",
        epilog=(
            "Examples:\n"
            "  signal-process generate --waveform sine --frequency 440 --duration 2 -o tone.wav\n"
            "  signal-process fft tone.wav --peaks 5\n"
            "  signal-process filter tone.wav --kind fir --type lowpass --cutoff 1000 --order 101\n"
            "  signal-process spectrogram tone.wav -o spectrogram.png\n"
            "  signal-process analyze tone.wav\n"
            "  signal-process detect tone.wav --method threshold --threshold 0.5\n"
            "  signal-process convert tone.wav --format csv -o tone.csv\n"
            "  signal-process demo\n"
            "  signal-process lab"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="generate a synthetic signal and save it (wav/csv)")
    p.add_argument("--waveform",
                   choices=["sine", "cosine", "square", "triangle", "sawtooth",
                            "chirp", "white-noise", "gaussian-noise"],
                   default="sine")
    p.add_argument("--frequency", type=float, default=440.0, help="frequency in Hz (f0 for chirp)")
    p.add_argument("--end-frequency", type=float, default=2_000.0, help="chirp end frequency (Hz)")
    p.add_argument("--amplitude", type=float, default=1.0)
    p.add_argument("--phase", type=float, default=0.0, help="phase offset (radians)")
    p.add_argument("--duration", type=float, default=1.0, help="duration (seconds)")
    p.add_argument("--sampling-rate", type=float, default=8_000.0, help="sampling rate (Hz)")
    p.add_argument("--chirp-kind", choices=["linear", "logarithmic", "quadratic"], default="linear")
    p.add_argument("--noise-amplitude", type=float, default=0.0, help="add white noise at this amplitude")
    p.add_argument("--seed", type=int, default=None, help="random seed for reproducible noise")
    p.add_argument("-o", "--output", default="signal.wav", help="output path (.wav or .csv)")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("fft", help="compute the FFT of a signal file")
    p.add_argument("input", help="input .wav/.csv/.json file")
    p.add_argument("-o", "--output", default=None, help="save a spectrum figure (png/pdf)")
    p.add_argument("--json", default=None, help="save machine-readable results as JSON")
    p.add_argument("--peaks", type=int, default=5, help="number of dominant peaks to report")
    p.set_defaults(func=cmd_fft)

    p = sub.add_parser("filter", help="design and apply a filter to a signal file")
    p.add_argument("input")
    p.add_argument("--kind", choices=["fir", "iir"], default="fir")
    p.add_argument("--type", choices=["lowpass", "highpass", "bandpass", "bandstop"], default="lowpass")
    p.add_argument("--cutoff", type=float, default=1_000.0, help="cutoff (Hz) for low/high-pass")
    p.add_argument("--cutoff-low", type=float, default=300.0, help="lower cutoff (Hz) for band-pass/stop")
    p.add_argument("--cutoff-high", type=float, default=3_000.0, help="upper cutoff (Hz) for band-pass/stop")
    p.add_argument("--order", type=int, default=101, help="FIR taps or IIR order")
    p.add_argument("--window", default="hamming", help="FIR window: hann/hamming/blackman/kaiser")
    p.add_argument("--causal", action="store_true", help="use causal filtering (default: zero-phase)")
    p.add_argument("-o", "--output", default="filtered.wav")
    p.add_argument("--response", default=None, help="save the frequency response figure")
    p.set_defaults(func=cmd_filter)

    p = sub.add_parser("spectrogram", help="compute and optionally render an STFT spectrogram")
    p.add_argument("input")
    p.add_argument("-o", "--output", default=None, help="save a spectrogram figure")
    p.add_argument("--json", default=None, help="save the spectrogram as JSON")
    p.add_argument("--nperseg", type=int, default=256)
    p.add_argument("--hop", type=int, default=128)
    p.add_argument("--window", default="hann")
    p.set_defaults(func=cmd_spectrogram)

    p = sub.add_parser("analyze", help="statistical and spectral analysis of a signal file")
    p.add_argument("input")
    p.add_argument("--json", default=None, help="save the AnalysisResult as JSON")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("detect", help="detect events in a signal file")
    p.add_argument("input")
    p.add_argument("--method", choices=["threshold", "adaptive", "peak"], default="threshold")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--rms-multiplier", type=float, default=2.0, help="adaptive threshold = rms * multiplier")
    p.add_argument("--min-distance", type=int, default=64, help="minimum peak separation (samples)")
    p.add_argument("--prominence", type=float, default=0.1)
    p.add_argument("-o", "--output", default=None, help="save a waveform figure with event markers")
    p.add_argument("--json", default=None, help="save events as JSON")
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("convert", help="convert between wav/csv/json")
    p.add_argument("input")
    p.add_argument("--format", choices=["wav", "csv", "json"], default=None,
                   help="defaults to the output extension")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_convert)

    p = sub.add_parser("demo", help="run the end-to-end demo pipeline into a folder")
    p.add_argument("-o", "--output", default="demo_output")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("lab", help="launch the Streamlit laboratory")
    p.add_argument("--port", type=int, default=None)
    p.set_defaults(func=cmd_lab)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())

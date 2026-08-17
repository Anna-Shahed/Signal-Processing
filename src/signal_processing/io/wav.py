"""WAV audio import and export via soundfile."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from ..core import Signal, SignalIOError
from ..utils.validation import SignalValidationError


def write_wav(
    signal: Signal,
    path: str | Path,
    *,
    subtype: str = "PCM_16",
    normalize: bool = True,
) -> Path:
    """Write a :class:`Signal` to a WAV file.

    Mono signals are written as-is. When ``normalize`` is true and the peak
    exceeds 1.0 the samples are scaled down so the file is not clipped.
    """
    out = Path(path)
    if out.suffix.lower() not in {".wav", ".flac", ".ogg", ".opus"}:
        out = out.with_suffix(".wav")

    samples = np.asarray(signal.samples, dtype=float)
    if samples.ndim == 1:
        samples = samples.reshape(-1, 1)

    if normalize:
        peak = float(np.max(np.abs(samples), initial=0.0))
        if peak > 1.0:
            samples = samples / peak

    try:
        sf.write(str(out), samples, int(round(signal.sampling_rate)), subtype=subtype)
    except Exception as exc:  # noqa: BLE001 - normalize soundfile errors
        raise SignalIOError(f"Failed to write audio to {out}: {exc}") from exc
    return out


def read_wav(
    path: str | Path,
    *,
    channel: int = 0,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Read a WAV file into a :class:`Signal`."""
    out = Path(path)
    if not out.is_file():
        raise SignalIOError(f"Audio file not found: {out}")

    try:
        data, rate = sf.read(str(out), always_2d=True)
        info = sf.info(str(out))
    except Exception as exc:  # noqa: BLE001 - normalize soundfile errors
        raise SignalIOError(f"Failed to read audio from {out}: {exc}") from exc

    if channel >= data.shape[1]:
        raise SignalValidationError(
            f"Requested channel {channel} but file has {data.shape[1]} channel(s)."
        )
    samples = np.asarray(data[:, channel], dtype=float)
    return Signal(
        samples=samples,
        sampling_rate=float(rate),
        name=name or out.stem,
        units=units,
        metadata={
            "source": str(out),
            "format": "wav",
            "channels": int(data.shape[1]),
            "channel": int(channel),
            "subtype": info.subtype,
        },
    )

"""Short-time Fourier transform and overlap-add reconstruction."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import get_window

from ..core import Signal, Spectrogram
from ..utils.validation import SignalValidationError, TransformError


def _as_real_vector(values: Signal | Any) -> tuple[np.ndarray, float, float]:
    """Return samples, sampling rate, and start time."""
    if isinstance(values, Signal):
        samples = np.asarray(values.samples, dtype=float)
        if samples.ndim != 1:
            raise TransformError("STFT currently requires a one-dimensional signal.")
        return samples, values.sampling_rate, values.start_time

    samples = np.asarray(values, dtype=float)
    if samples.ndim != 1 or samples.size == 0:
        raise TransformError("STFT input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise TransformError("STFT input must contain finite values.")
    return samples, 1.0, 0.0


def _window_values(
    window: str | tuple[Any, ...] | np.ndarray,
    length: int,
) -> tuple[np.ndarray, str]:
    """Resolve a named or custom analysis window."""
    if isinstance(window, np.ndarray):
        values = np.asarray(window, dtype=float)
        if values.ndim != 1 or values.size != length:
            raise SignalValidationError(
                "A custom STFT window must be one-dimensional and match nperseg."
            )
        return values, "custom"

    try:
        values = np.asarray(get_window(window, length, fftbins=True), dtype=float)
    except ValueError as exc:
        raise SignalValidationError(f"Invalid STFT window: {window!r}.") from exc
    return values, str(window)


def stft(
    values: Signal | Any,
    *,
    sampling_rate: float | None = None,
    nperseg: int = 256,
    hop_length: int | None = None,
    window: str | tuple[Any, ...] | np.ndarray = "hann",
    nfft: int | None = None,
    one_sided: bool = True,
) -> Spectrogram:
    """Compute an STFT and return a :class:`Spectrogram`.

    Frames are centered through zero-padding at both boundaries. This makes
    overlap-add reconstruction well behaved for common windows such as Hann.
    """
    samples, signal_rate, start_time = _as_real_vector(values)
    rate = signal_rate if sampling_rate is None else float(sampling_rate)

    if not np.isfinite(rate) or rate <= 0:
        raise SignalValidationError("sampling_rate must be positive and finite.")

    nperseg = int(nperseg)
    if nperseg <= 0:
        raise SignalValidationError("nperseg must be positive.")

    hop = nperseg // 2 if hop_length is None else int(hop_length)
    if hop <= 0 or hop > nperseg:
        raise SignalValidationError("hop_length must be between 1 and nperseg.")

    transform_length = nperseg if nfft is None else int(nfft)
    if transform_length < nperseg:
        raise SignalValidationError("nfft must be at least nperseg.")

    analysis_window, window_name = _window_values(window, nperseg)
    pad_left = nperseg // 2
    padded = np.pad(samples, (pad_left, pad_left), mode="constant")

    n_frames = max(1, int(np.ceil((padded.size - nperseg) / hop)) + 1)
    required_size = (n_frames - 1) * hop + nperseg
    if required_size > padded.size:
        padded = np.pad(padded, (0, required_size - padded.size))

    frames = np.empty((n_frames, nperseg), dtype=float)
    for frame_index in range(n_frames):
        start = frame_index * hop
        frames[frame_index] = padded[start : start + nperseg] * analysis_window

    if one_sided:
        values_out = np.fft.rfft(frames, n=transform_length, axis=1).T
        frequencies = np.fft.rfftfreq(transform_length, d=1.0 / rate)
    else:
        values_out = np.fft.fft(frames, n=transform_length, axis=1).T
        frequencies = np.fft.fftfreq(transform_length, d=1.0 / rate)

    frame_centers = (
        np.arange(n_frames) * hop - pad_left + nperseg / 2
    ) / rate + start_time

    return Spectrogram(
        times=frame_centers,
        frequencies=frequencies,
        values=values_out,
        sampling_rate=rate,
        window=window_name,
        hop_length=hop,
        one_sided=one_sided,
        metadata={
            "nperseg": nperseg,
            "nfft": transform_length,
            "pad_left": pad_left,
            "original_length": samples.size,
            "start_time": start_time,
            "window_values": analysis_window.tolist(),
        },
    )


def istft(
    spectrogram: Spectrogram,
    *,
    length: int | None = None,
) -> Signal:
    """Reconstruct a signal from a :class:`Spectrogram` by overlap-add."""
    if not isinstance(spectrogram, Spectrogram):
        raise TransformError("istft requires a Spectrogram instance.")

    nperseg = int(spectrogram.metadata.get("nperseg", 0))
    nfft = int(spectrogram.metadata.get("nfft", 0))
    pad_left = int(spectrogram.metadata.get("pad_left", 0))
    original_length = int(
        spectrogram.metadata.get("original_length", spectrogram.times.size)
    )
    start_time = float(spectrogram.metadata.get("start_time", 0.0))

    if nperseg <= 0 or nfft < nperseg:
        raise TransformError("Spectrogram metadata does not contain valid FFT lengths.")

    if "window_values" in spectrogram.metadata:
        window = np.asarray(spectrogram.metadata["window_values"], dtype=float)
    else:
        window, _ = _window_values(spectrogram.window, nperseg)

    n_frames = spectrogram.values.shape[1]
    hop = spectrogram.hop_length
    output_length = (n_frames - 1) * hop + nperseg

    reconstructed = np.zeros(output_length, dtype=float)
    window_energy = np.zeros(output_length, dtype=float)

    for frame_index in range(n_frames):
        spectrum_column = spectrogram.values[:, frame_index]
        if spectrogram.one_sided:
            frame = np.fft.irfft(spectrum_column, n=nfft)[:nperseg]
        else:
            frame = np.fft.ifft(spectrum_column, n=nfft).real[:nperseg]

        start = frame_index * hop
        reconstructed[start : start + nperseg] += frame * window
        window_energy[start : start + nperseg] += window**2

    valid = window_energy > np.finfo(float).eps
    reconstructed[valid] /= window_energy[valid]

    start = min(max(pad_left, 0), reconstructed.size)
    target_length = original_length if length is None else int(length)
    if target_length <= 0:
        raise SignalValidationError("length must be positive.")

    stop = min(start + target_length, reconstructed.size)
    samples = reconstructed[start:stop]

    if samples.size < target_length:
        samples = np.pad(samples, (0, target_length - samples.size))

    return Signal(
        samples=samples,
        sampling_rate=spectrogram.sampling_rate,
        start_time=start_time,
        name="istft_reconstruction",
        metadata={
            "source": "istft",
            "nperseg": nperseg,
            "hop_length": hop,
        },
    )

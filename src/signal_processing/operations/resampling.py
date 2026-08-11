from __future__ import annotations

from fractions import Fraction

import numpy as np
from scipy.signal import resample_poly

from ..core import Signal
from ..utils.validation import SignalValidationError, validate_sampling_rate


def _as_1d_signal(
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
                "sampling_rate is required when resampling a plain array."
            )
        rate = validate_sampling_rate(sampling_rate)
        start_time = 0.0

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError(
            "Resampling requires a non-empty one-dimensional input."
        )
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError("Input must contain finite values.")
    return samples, rate, start_time


def resample(
    signal: Signal | np.ndarray,
    sampling_rate: float,
    *,
    input_sampling_rate: float | None = None,
    max_denominator: int = 10000,
    name: str = "resampled",
) -> Signal:
    """Resample to a new uniform sampling rate using a rational polyphase filter.

    A low-pass anti-aliasing filter is applied automatically by
    ``resample_poly``, which upsamples, filters, and downsamples using the
    rational approximation of the rate ratio.
    """
    samples, current_rate, start_time = _as_1d_signal(signal, input_sampling_rate)
    new_rate = validate_sampling_rate(sampling_rate)

    if np.isclose(new_rate, current_rate):
        return Signal(
            samples=samples,
            sampling_rate=current_rate,
            start_time=start_time,
            name=name,
            metadata={"resampled": False},
        )

    ratio = Fraction(new_rate / current_rate).limit_denominator(max_denominator)
    if ratio.numerator <= 0 or ratio.denominator <= 0:
        raise SignalValidationError("Resampling ratio must be positive.")

    resampled = resample_poly(
        samples,
        up=ratio.numerator,
        down=ratio.denominator,
        axis=0,
    )

    return Signal(
        samples=resampled,
        sampling_rate=new_rate,
        start_time=start_time,
        name=name,
        metadata={
            "resampled": True,
            "input_sampling_rate": current_rate,
            "output_sampling_rate": new_rate,
            "up": ratio.numerator,
            "down": ratio.denominator,
        },
    )


def downsample(
    signal: Signal | np.ndarray,
    factor: int,
    *,
    input_sampling_rate: float | None = None,
    name: str = "downsampled",
) -> Signal:
    """Decimate by an integer factor after anti-alias low-pass filtering."""
    factor = int(factor)
    if factor < 1:
        raise SignalValidationError("Downsampling factor must be a positive integer.")

    samples, rate, start_time = _as_1d_signal(signal, input_sampling_rate)

    if factor == 1:
        return Signal(samples=samples, sampling_rate=rate, start_time=start_time, name=name)

    from scipy.signal import decimate

    decimated = decimate(samples, q=factor, ftype="fir", zero_phase=True)
    return Signal(
        samples=decimated,
        sampling_rate=rate / factor,
        start_time=start_time,
        name=name,
        metadata={"operation": "downsample", "factor": factor},
    )


def upsample(
    signal: Signal | np.ndarray,
    factor: int,
    *,
    input_sampling_rate: float | None = None,
    name: str = "upsampled",
) -> Signal:
    """Upsample by an integer factor using polyphase interpolation."""
    factor = int(factor)
    if factor < 1:
        raise SignalValidationError("Upsampling factor must be a positive integer.")

    samples, rate, start_time = _as_1d_signal(signal, input_sampling_rate)

    if factor == 1:
        return Signal(samples=samples, sampling_rate=rate, start_time=start_time, name=name)

    resampled = resample_poly(samples, up=factor, down=1, axis=0)
    return Signal(
        samples=resampled,
        sampling_rate=rate * factor,
        start_time=start_time,
        name=name,
        metadata={"operation": "upsample", "factor": factor},
    )

"""Core sampled-signal data model."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, overload

import numpy as np
from scipy.signal import resample_poly

from ..utils.validation import (
    SignalValidationError,
    validate_metadata,
    validate_real_array,
    validate_sampling_rate,
)


@dataclass(slots=True)
class Signal:
    """A uniformly sampled real-valued signal.

    Samples may be one-dimensional with shape ``(n_samples,)`` or
    multichannel with shape ``(n_samples, n_channels)``. Time is represented
    by ``start_time + sample_index / sampling_rate``.
    """

    samples: np.ndarray | Sequence[float]
    sampling_rate: float
    start_time: float = 0.0
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    units: str | None = None

    def __post_init__(self) -> None:
        self.samples = validate_real_array(self.samples, name="samples")
        self.sampling_rate = validate_sampling_rate(self.sampling_rate)

        self.start_time = float(self.start_time)
        if not np.isfinite(self.start_time):
            raise SignalValidationError("start_time must be finite.")

        self.metadata = validate_metadata(self.metadata)

        if self.name is not None:
            self.name = str(self.name)

        if self.units is not None:
            self.units = str(self.units)

    @property
    def n_samples(self) -> int:
        """Return the number of samples."""
        return int(self.samples.shape[0])

    @property
    def n_channels(self) -> int:
        """Return the number of channels."""
        return 1 if self.samples.ndim == 1 else int(self.samples.shape[1])

    @property
    def duration(self) -> float:
        """Return the signal duration in seconds."""
        return self.n_samples / self.sampling_rate

    @property
    def time(self) -> np.ndarray:
        """Return sample timestamps in seconds."""
        return self.start_time + np.arange(self.n_samples) / self.sampling_rate

    @property
    def mean(self) -> float | np.ndarray:
        """Return the arithmetic mean, computed per channel."""
        value = np.mean(self.samples, axis=0)
        return float(value) if self.samples.ndim == 1 else value

    @property
    def rms(self) -> float | np.ndarray:
        """Return the root-mean-square amplitude, computed per channel."""
        value = np.sqrt(np.mean(np.square(self.samples), axis=0))
        return float(value) if self.samples.ndim == 1 else value

    @property
    def variance(self) -> float | np.ndarray:
        """Return the population variance, computed per channel."""
        value = np.var(self.samples, axis=0)
        return float(value) if self.samples.ndim == 1 else value

    @property
    def standard_deviation(self) -> float | np.ndarray:
        """Return the population standard deviation, computed per channel."""
        value = np.std(self.samples, axis=0)
        return float(value) if self.samples.ndim == 1 else value

    @property
    def peak_amplitude(self) -> float | np.ndarray:
        """Return the maximum absolute amplitude, computed per channel."""
        value = np.max(np.abs(self.samples), axis=0)
        return float(value) if self.samples.ndim == 1 else value

    def copy(self, **changes: Any) -> Signal:
        """Return an independent copy with optional field replacements."""
        values: dict[str, Any] = {
            "samples": self.samples.copy(),
            "sampling_rate": self.sampling_rate,
            "start_time": self.start_time,
            "name": self.name,
            "metadata": dict(self.metadata),
            "units": self.units,
        }
        values.update(changes)
        return Signal(**values)

    def normalize(
        self,
        mode: str = "peak",
        target: float = 1.0,
    ) -> Signal:
        """Return a normalized copy.

        Parameters
        ----------
        mode:
            ``"peak"`` scales by the largest absolute sample.
            ``"rms"`` scales by the RMS amplitude.
        target:
            Desired peak or RMS amplitude.
        """
        if target <= 0 or not np.isfinite(target):
            raise SignalValidationError(
                "target must be finite and greater than zero."
            )

        mode = mode.lower()

        if mode == "peak":
            scale = float(np.max(np.abs(self.samples)))
        elif mode == "rms":
            scale = float(np.sqrt(np.mean(np.square(self.samples))))
        else:
            raise SignalValidationError(
                "mode must be either 'peak' or 'rms'."
            )

        if scale == 0:
            raise SignalValidationError(
                "Cannot normalize an all-zero signal."
            )

        return self.copy(samples=self.samples * (target / scale))

    def slice(self, start: int, stop: int) -> Signal:
        """Return a sample-index slice while preserving absolute time."""
        if not isinstance(start, int) or not isinstance(stop, int):
            raise SignalValidationError(
                "start and stop must be integer sample indices."
            )

        selected = self.samples[start:stop]

        if selected.shape[0] == 0:
            raise SignalValidationError(
                "The requested slice is empty."
            )

        normalized_start = (
            start if start >= 0 else max(0, self.n_samples + start)
        )

        return self.copy(
            samples=selected,
            start_time=(
                self.start_time
                + normalized_start / self.sampling_rate
            ),
        )

    def resample(
        self,
        sampling_rate: float,
        *,
        max_denominator: int = 10000,
    ) -> Signal:
        """Resample the signal using polyphase filtering."""
        new_rate = validate_sampling_rate(sampling_rate)

        if np.isclose(new_rate, self.sampling_rate):
            return self.copy()

        ratio = Fraction(
            new_rate / self.sampling_rate
        ).limit_denominator(max_denominator)

        resampled = resample_poly(
            self.samples,
            up=ratio.numerator,
            down=ratio.denominator,
            axis=0,
        )

        metadata = dict(self.metadata)
        metadata["resampled_from"] = self.sampling_rate

        return self.copy(
            samples=resampled,
            sampling_rate=new_rate,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the signal to JSON-compatible data."""
        return {
            "samples": self.samples.tolist(),
            "sampling_rate": self.sampling_rate,
            "start_time": self.start_time,
            "name": self.name,
            "metadata": self.metadata,
            "units": self.units,
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize the signal to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Signal:
        """Construct a signal from serialized data."""
        required = {"samples", "sampling_rate"}
        missing = required.difference(data)

        if missing:
            raise SignalValidationError(
                f"Missing signal fields: {sorted(missing)}."
            )

        return cls(**data)

    @classmethod
    def from_json(cls, text: str) -> Signal:
        """Construct a signal from JSON text."""
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SignalValidationError(
                "Invalid signal JSON."
            ) from exc

        if not isinstance(data, dict):
            raise SignalValidationError(
                "Signal JSON must contain an object."
            )

        return cls.from_dict(data)

    @overload
    def __getitem__(self, item: int) -> float | np.ndarray:
        ...

    @overload
    def __getitem__(self, item: slice) -> Signal:
        ...

    def __getitem__(
        self,
        item: int | slice,
    ) -> float | np.ndarray | Signal:
        """Access a sample or return a time-correct slice."""
        if isinstance(item, slice):
            start, stop, step = item.indices(self.n_samples)

            if step != 1:
                selected = self.samples[item]

                return self.copy(
                    samples=selected,
                    start_time=(
                        self.time[start]
                        if selected.shape[0]
                        else self.start_time
                    ),
                )

            return self.slice(start, stop)

        return self.samples[item]

    def _binary_operation(
        self,
        other: Any,
        operation: Any,
        symbol: str,
    ) -> Signal:
        if isinstance(other, Signal):
            if not np.isclose(
                self.sampling_rate,
                other.sampling_rate,
            ):
                raise SignalValidationError(
                    f"Cannot apply '{symbol}' to signals with "
                    "different sampling rates."
                )

            if self.samples.shape != other.samples.shape:
                raise SignalValidationError(
                    f"Cannot apply '{symbol}' to signals with "
                    "different shapes."
                )

            values = operation(self.samples, other.samples)
        else:
            values = operation(self.samples, other)

        return self.copy(samples=values)

    def __add__(self, other: Any) -> Signal:
        return self._binary_operation(other, np.add, "+")

    def __sub__(self, other: Any) -> Signal:
        return self._binary_operation(other, np.subtract, "-")

    def __mul__(self, other: Any) -> Signal:
        return self._binary_operation(other, np.multiply, "*")

    def __truediv__(self, other: Any) -> Signal:
        return self._binary_operation(other, np.divide, "/")

    def __array__(self, dtype: Any = None) -> np.ndarray:
        return np.asarray(self.samples, dtype=dtype)

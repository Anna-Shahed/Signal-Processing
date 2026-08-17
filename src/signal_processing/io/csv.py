"""CSV import and export for :class:`~signal_processing.core.signal.Signal`."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..core import Signal, SignalIOError
from ..utils.validation import SignalValidationError


def write_csv(
    signal: Signal,
    path: str | Path,
    *,
    include_time: bool = True,
    columns: tuple[str, str] = ("time", "value"),
) -> Path:
    """Write a :class:`Signal` to CSV.

    Parameters
    ----------
    signal:
        Signal to export.
    path:
        Destination path; a ``.csv`` suffix is appended when missing.
    include_time:
        When ``True`` the first column is the time axis; otherwise only
        the samples are written.
    columns:
        Column names used when ``include_time`` is true.
    """
    out = Path(path)
    if out.suffix.lower() != ".csv":
        out = out.with_suffix(".csv")

    data: dict[str, np.ndarray]
    if include_time:
        data = {columns[0]: np.asarray(signal.time, dtype=float),
                columns[1]: np.asarray(signal.samples, dtype=float)}
    else:
        data = {columns[1]: np.asarray(signal.samples, dtype=float)}

    try:
        pd.DataFrame(data).to_csv(out, index=False)
    except OSError as exc:  # pragma: no cover - environment dependent
        raise SignalIOError(f"Failed to write CSV to {out}: {exc}") from exc
    return out


def read_csv(
    path: str | Path,
    *,
    sampling_rate: float | None = None,
    time_column: str | None = None,
    value_column: str | None = None,
    name: str | None = None,
    units: str | None = None,
) -> Signal:
    """Read a CSV file into a :class:`Signal`.

    Two layouts are supported:

    * ``time,value`` pairs — the sampling rate is inferred from the median
      time step (an explicit ``sampling_rate`` takes precedence).
    * samples only — ``sampling_rate`` must then be supplied.
    """
    out = Path(path)
    if not out.is_file():
        raise SignalIOError(f"CSV file not found: {out}")

    try:
        frame = pd.read_csv(out)
    except Exception as exc:  # noqa: BLE001 - normalize pandas errors
        raise SignalIOError(f"Failed to parse CSV {out}: {exc}") from exc

    if frame.shape[1] < 1:
        raise SignalValidationError("CSV must contain at least one column.")

    if frame.shape[1] >= 2:
        time_col = time_column or frame.columns[0]
        value_col = value_column or frame.columns[1]
        times = np.asarray(frame[time_col], dtype=float)
        samples = np.asarray(frame[value_col], dtype=float)
        if sampling_rate is None:
            steps = np.diff(times)
            steps = steps[np.isfinite(steps) & (steps > 0)]
            if steps.size == 0:
                raise SignalValidationError(
                    "Cannot infer a sampling rate from the time column; "
                    "pass sampling_rate explicitly."
                )
            sampling_rate = float(1.0 / np.median(steps))
        start_time = float(times[0]) if times.size else 0.0
        return Signal(
            samples=samples,
            sampling_rate=sampling_rate,
            start_time=start_time,
            name=name or out.stem,
            units=units,
            metadata={"source": str(out), "format": "csv"},
        )

    if sampling_rate is None:
        raise SignalValidationError(
            "sampling_rate is required when the CSV contains samples only."
        )
    samples = np.asarray(frame.iloc[:, 0], dtype=float)
    return Signal(
        samples=samples,
        sampling_rate=sampling_rate,
        name=name or out.stem,
        units=units,
        metadata={"source": str(out), "format": "csv", "samples_only": True},
    )

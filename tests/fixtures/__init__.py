"""Deterministic reference implementations used by the test-suite.

Importable as ``from fixtures import ...`` because pytest inserts the
``tests/`` directory onto ``sys.path`` (unit/integration/property are
packages containing ``__init__.py``).
"""

from __future__ import annotations

import numpy as np


def reference_circular_convolution(a, b):
    """O(N²) reference for circular convolution, matching numpy semantics."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n = max(a.size, b.size)
    A = np.zeros(n)
    B = np.zeros(n)
    A[: a.size] = a
    B[: b.size] = b
    return np.array([sum(A[k] * B[(m - k) % n] for k in range(n)) for m in range(n)])


def reference_snr_db(signal: float, noise: float) -> float:
    """20*log10(rms_signal / rms_noise)."""
    from signal_processing import Signal

    if isinstance(signal, Signal):
        signal = signal.samples
    if isinstance(noise, Signal):
        noise = noise.samples
    rms_s = float(np.sqrt(np.mean(np.asarray(signal) ** 2)))
    rms_n = float(np.sqrt(np.mean(np.asarray(noise) ** 2)))
    return 20.0 * np.log10(rms_s / rms_n)

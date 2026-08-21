"""Kalman filter: convergence on a controlled constant signal."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing.estimation.kalman import KalmanFilter


def test_kalman_converges_on_constant():
    rng = np.random.default_rng(42)
    true_value = 5.0
    measurements = true_value + rng.normal(0.0, 1.0, size=500)

    kf = KalmanFilter(
        state_transition=np.array([[1.0]]),
        observation_matrix=np.array([[1.0]]),
        process_covariance=np.array([[1e-4]]),
        observation_covariance=np.array([[1.0]]),
        initial_state=np.array([0.0]),
        initial_covariance=np.array([[1.0]]),
    )
    estimates = kf.filter(measurements)
    assert estimates.shape == (500, 1)
    # The filter should have converged near the truth by the final samples.
    assert abs(float(estimates[-10:].mean()) - true_value) < 0.3


def test_kalman_tracks_step_change():
    rng = np.random.default_rng(7)
    true = np.concatenate([np.full(200, 1.0), np.full(300, 4.0)])
    measurements = true + rng.normal(0.0, 0.5, size=true.size)

    kf = KalmanFilter(
        state_transition=np.array([[1.0]]),
        observation_matrix=np.array([[1.0]]),
        process_covariance=np.array([[1e-2]]),
        observation_covariance=np.array([[0.25]]),
        initial_state=np.array([0.0]),
        initial_covariance=np.array([[1.0]]),
    )
    estimates = kf.filter(measurements)
    assert abs(float(estimates[-10:].mean()) - 4.0) < 0.3

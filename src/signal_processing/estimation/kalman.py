"""Reusable Kalman filter for scalar and vector state spaces."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..utils.validation import SignalValidationError


@dataclass(slots=True)
class KalmanFilter:
    """Discrete-time linear Kalman filter.

    State model::

        x[k]     = F x[k-1] + w[k],   w ~ N(0, Q)
        z[k]     = H x[k]   + v[k],   v ~ N(0, R)

    The filter alternates between ``predict`` and ``update`` calls and
    maintains the posterior state estimate and covariance after each update.
    """

    state_transition: np.ndarray
    observation_matrix: np.ndarray
    process_covariance: np.ndarray
    observation_covariance: np.ndarray
    state_estimate: np.ndarray
    covariance: np.ndarray
    control_matrix: np.ndarray | None = None

    def __post_init__(self) -> None:
        self.state_transition = np.atleast_2d(np.asarray(self.state_transition, dtype=float))
        self.observation_matrix = np.atleast_2d(np.asarray(self.observation_matrix, dtype=float))
        self.process_covariance = np.atleast_2d(np.asarray(self.process_covariance, dtype=float))
        self.observation_covariance = np.atleast_2d(np.asarray(self.observation_covariance, dtype=float))
        self.state_estimate = np.asarray(self.state_estimate, dtype=float)
        self.covariance = np.atleast_2d(np.asarray(self.covariance, dtype=float))

        state_dim = self.state_transition.shape[0]
        observation_dim = self.observation_matrix.shape[0]

        if self.state_transition.shape != (state_dim, state_dim):
            raise SignalValidationError("state_transition must be a square matrix.")
        if self.observation_matrix.shape != (observation_dim, state_dim):
            raise SignalValidationError(
                "observation_matrix must have shape (observation_dim, state_dim)."
            )
        if self.process_covariance.shape != (state_dim, state_dim):
            raise SignalValidationError("process_covariance must be (state_dim, state_dim).")
        if self.observation_covariance.shape != (observation_dim, observation_dim):
            raise SignalValidationError(
                "observation_covariance must be (observation_dim, observation_dim)."
            )
        if self.state_estimate.shape != (state_dim,):
            raise SignalValidationError("state_estimate must have shape (state_dim,).")
        if self.covariance.shape != (state_dim, state_dim):
            raise SignalValidationError("covariance must be (state_dim, state_dim).")
        if self.control_matrix is not None:
            self.control_matrix = np.atleast_2d(np.asarray(self.control_matrix, dtype=float))
            if self.control_matrix.shape != (state_dim, self.control_matrix.shape[1]):
                raise SignalValidationError("control_matrix has an incompatible shape.")

        if np.any(np.diag(self.process_covariance) < 0):
            raise SignalValidationError("process_covariance must be positive semidefinite.")
        if np.any(np.diag(self.observation_covariance) < 0):
            raise SignalValidationError("observation_covariance must be positive semidefinite.")

    def predict(self, control_input: np.ndarray | None = None) -> KalmanFilter:
        """Advance the state prediction and covariance."""
        self.state_estimate = self.state_transition @ self.state_estimate
        if control_input is not None and self.control_matrix is not None:
            self.state_estimate = (
                self.state_estimate + self.control_matrix @ np.asarray(control_input, dtype=float)
            )
        self.covariance = (
            self.state_transition @ self.covariance @ self.state_transition.T
            + self.process_covariance
        )
        return self

    def update(self, observation: float | np.ndarray) -> KalmanFilter:
        """Incorporate a measurement into the state estimate."""
        observation = np.asarray(observation, dtype=float).reshape(-1)
        observation_dim = self.observation_matrix.shape[0]
        if observation.shape != (observation_dim,):
            raise SignalValidationError(
                f"observation must have shape ({observation_dim},)."
            )

        innovation_covariance = (
            self.observation_matrix @ self.covariance @ self.observation_matrix.T
            + self.observation_covariance
        )
        gain = (
            self.covariance
            @ self.observation_matrix.T
            @ np.linalg.inv(innovation_covariance)
        )

        innovation = observation - self.observation_matrix @ self.state_estimate
        self.state_estimate = self.state_estimate + gain @ innovation
        identity = np.eye(self.state_estimate.size)
        self.covariance = (identity - gain @ self.observation_matrix) @ self.covariance

        return self

    def filter(
        self,
        observations: np.ndarray,
        *,
        control_inputs: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Filter a sequence of observations.

        Returns a tuple ``(state_estimates, covariances)`` where the estimates
        have shape ``(n_observations, state_dim)`` and covariances are stacked
        along the leading axis.
        """
        observations = np.asarray(observations, dtype=float)
        if observations.ndim == 1:
            observations = observations.reshape(-1, 1)

        n_observations = observations.shape[0]
        estimates = np.zeros((n_observations, self.state_estimate.size), dtype=float)
        covariances = np.zeros(
            (n_observations, self.state_estimate.size, self.state_estimate.size),
            dtype=float,
        )

        for index in range(n_observations):
            self.predict(
                control_input=None if control_inputs is None else control_inputs[index]
            )
            self.update(observations[index])
            estimates[index] = self.state_estimate
            covariances[index] = self.covariance

        return estimates, covariances


def constant_velocity_kalman(
    *,
    process_noise: float = 1e-4,
    measurement_noise: float = 1e-2,
    initial_position: float = 0.0,
    initial_velocity: float = 0.0,
) -> KalmanFilter:
    """Create a 2-D constant-velocity Kalman filter for position tracking."""
    process_noise = float(process_noise)
    measurement_noise = float(measurement_noise)

    if process_noise <= 0 or measurement_noise <= 0:
        raise SignalValidationError("Noise variances must be positive.")

    return KalmanFilter(
        state_transition=np.array([[1.0, 1.0], [0.0, 1.0]]),
        observation_matrix=np.array([[1.0, 0.0]]),
        process_covariance=process_noise * np.eye(2),
        observation_covariance=np.array([[measurement_noise]]),
        state_estimate=np.array([initial_position, initial_velocity]),
        covariance=np.eye(2),
    )


def smooth_signal(
    signal: Signal | np.ndarray,
    *,
    sampling_rate: float | None = None,
    process_noise: float = 1e-4,
    measurement_noise: float | None = None,
) -> np.ndarray:
    """Smooth a one-dimensional signal with a constant-velocity Kalman filter.

    The measurement noise is estimated from the data when not supplied.
    """
    if isinstance(signal, Signal):
        samples = np.asarray(signal.samples, dtype=float)
    else:
        samples = np.asarray(signal, dtype=float)

    if samples.ndim != 1 or samples.size == 0:
        raise SignalValidationError("Input must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(samples)):
        raise SignalValidationError("Input must contain finite values.")

    if measurement_noise is None:
        measurement_noise = max(float(np.var(samples)) * 0.01, 1e-12)

    filter_instance = constant_velocity_kalman(
        process_noise=process_noise,
        measurement_noise=measurement_noise,
        initial_position=float(samples[0]),
    )
    estimates, _ = filter_instance.filter(samples)
    return estimates[:, 0]

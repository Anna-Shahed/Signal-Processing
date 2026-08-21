"""Composable pipeline: stage execution and metadata recording."""

from __future__ import annotations

import numpy as np
import pytest

from signal_processing import Signal
from signal_processing.pipelines import Pipeline, detrend, fft_stage, lowpass, normalize


def test_detrend_removes_linear_trend():
    x = np.linspace(-1.0, 1.0, 1_000)
    sig = Signal(x, sampling_rate=1_000)
    out = Pipeline().add(detrend()).run(sig)
    assert isinstance(out, Signal)
    assert abs(float(out.samples.mean())) < 1e-9
    assert abs(float(out.samples[0] - out.samples[-1])) < 1e-9


def test_full_pipeline_runs_and_records_metadata(noisy_tone):
    pipeline = (
        Pipeline()
        .add(detrend())
        .add(normalize())
        .add(lowpass(cutoff=100, order=4))
        .add(fft_stage(one_sided=True))
    )
    result = pipeline.run(noisy_tone)
    assert "dominant_frequency" in result.metrics
    assert len(pipeline.stage_metadata) == 4
    names = [m["stage"] for m in pipeline.stage_metadata]
    assert names == ["detrend", "normalize", "lowpass", "fft"]


def test_pipeline_metadata_has_execution_order(noisy_tone):
    pipeline = Pipeline().add(normalize()).add(lowpass(cutoff=100, order=4))
    pipeline.run(noisy_tone)
    for i, meta in enumerate(pipeline.stage_metadata):
        assert meta["index"] == i
        assert "duration_s" in meta

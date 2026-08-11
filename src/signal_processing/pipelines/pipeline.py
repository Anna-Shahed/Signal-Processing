"""Composable signal-processing pipeline engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core import AnalysisResult, Signal
from ..utils.validation import PipelineError
from .stages import Stage


@dataclass(slots=True)
class Pipeline:
    """Chain named processing stages and run them over a signal.

    A stage must accept a :class:`Signal` and return either a :class:`Signal`
    (which is passed to the next stage) or an :class:`AnalysisResult` (which
    is recorded and the previous signal continues unchanged).
    """

    stages: list[Stage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    _results: list[AnalysisResult] = field(default_factory=list, init=False)
    _history: list[dict[str, Any]] = field(default_factory=list, init=False)

    def add(self, stage: Stage) -> Pipeline:
        """Append a stage and return this pipeline for fluent composition."""
        if not hasattr(stage, "apply"):
            raise PipelineError("Each pipeline stage must provide an apply method.")
        self.stages.append(stage)
        return self

    def run(self, signal: Signal) -> AnalysisResult:
        """Execute every stage and return a consolidated result."""
        if not isinstance(signal, Signal):
            raise PipelineError("Pipeline input must be a Signal instance.")

        current = signal
        self._results = []
        self._history = []

        for stage in self.stages:
            try:
                output = stage.apply(current)
            except Exception as exc:
                raise PipelineError(f"Stage '{stage.name}' failed: {exc}") from exc

            if isinstance(output, Signal):
                current = output
                self._history.append(
                    {"stage": stage.name, "output_type": "signal", "n_samples": current.n_samples}
                )
            elif isinstance(output, AnalysisResult):
                self._results.append(output)
                self._history.append(
                    {
                        "stage": stage.name,
                        "output_type": "analysis_result",
                        "metrics": dict(output.metrics),
                    }
                )
            else:
                raise PipelineError(
                    f"Stage '{stage.name}' must return a Signal or AnalysisResult."
                )

        final = AnalysisResult(
            metrics={"n_stages": len(self.stages), "n_results": len(self._results)},
            metadata={
                "pipeline": True,
                "stages": [stage.name for stage in self.stages],
                "history": self._history,
            },
        )
        for result in self._results:
            final.metrics.update(result.metrics)
            final.arrays.update(result.arrays)
            final.metadata.update(result.metadata)
            final.warnings.extend(result.warnings)

        final.arrays["signal"] = current.samples
        final.metadata["final_signal"] = current.to_dict()
        return final

    def __call__(self, signal: Signal) -> AnalysisResult:
        """Allow ``pipeline(signal)`` as an alias for ``run``."""
        return self.run(signal)

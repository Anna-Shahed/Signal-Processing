from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Event:
    """A detected temporal event."""

    start_time: float
    end_time: float
    peak_time: float
    amplitude: float
    confidence: float = 1.0
    event_type: str = "event"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.start_time = float(self.start_time)
        self.end_time = float(self.end_time)
        self.peak_time = float(self.peak_time)
        self.amplitude = float(self.amplitude)
        self.confidence = float(self.confidence)
        self.event_type = str(self.event_type)

        if self.end_time < self.start_time:
            raise ValueError("end_time must not precede start_time.")
        if not self.start_time <= self.peak_time <= self.end_time:
            raise ValueError("peak_time must lie inside the event interval.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between zero and one.")
        self.metadata = dict(self.metadata)

    @property
    def duration(self) -> float:
        """Event duration in seconds."""
        return self.end_time - self.start_time

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "peak_time": self.peak_time,
            "amplitude": self.amplitude,
            "duration": self.duration,
            "confidence": self.confidence,
            "event_type": self.event_type,
            "metadata": self.metadata,
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize the event to JSON."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        """Construct an event from serialized data."""
        fields = {
            "start_time",
            "end_time",
            "peak_time",
            "amplitude",
        }
        missing = fields.difference(data)
        if missing:
            raise ValueError(f"Missing event fields: {sorted(missing)}.")
        return cls(
            start_time=data["start_time"],
            end_time=data["end_time"],
            peak_time=data["peak_time"],
            amplitude=data["amplitude"],
            confidence=data.get("confidence", 1.0),
            event_type=data.get("event_type", "event"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, text: str) -> Event:
        """Construct an event from JSON text."""
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Event JSON must contain an object.")
        return cls.from_dict(data)

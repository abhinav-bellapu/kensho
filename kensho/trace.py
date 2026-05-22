"""In-memory trace logging for benchmark runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class TraceEvent:
    step_index: int
    event_type: str
    timestamp: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_index": self.step_index,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class TraceLogger:
    """Records a structured timeline of events during a run."""

    def __init__(self) -> None:
        self._events: list[TraceEvent] = []
        self._next_index = 0

    def log(self, event_type: str, payload: dict[str, Any] | None = None) -> TraceEvent:
        event = TraceEvent(
            step_index=self._next_index,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=dict(payload or {}),
        )
        self._next_index += 1
        self._events.append(event)
        return event

    def list_events(self) -> list[TraceEvent]:
        return list(self._events)

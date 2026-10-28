"""Structured traces for each Agent tool call."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


def compact_payload(value: Any, max_chars: int = 6000) -> Any:
    """Keep traces useful without allowing a huge result to dominate output."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        encoded = str(value)

    if len(encoded) <= max_chars:
        return value

    return {
        "truncated": True,
        "preview": encoded[:max_chars],
        "original_json_chars": len(encoded),
    }


@dataclass(frozen=True)
class AgentToolTrace:
    model_turn: int
    tool_call_id: str
    tool_name: str
    arguments: dict[str, Any]
    status: str
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentRunResult:
    answer: str
    model_turns: int
    tool_traces: list[AgentToolTrace] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "model_turns": self.model_turns,
            "tool_calls": [trace.to_dict() for trace in self.tool_traces],
        }

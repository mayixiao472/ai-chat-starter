"""Tool allowlists and OpenAI-compatible tool schema conversion."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from mcp.types import Tool


READ_ONLY_TOOL_NAMES = frozenset(
    {
        "faucet_list_services",
        "faucet_list_tables",
        "faucet_describe_table",
        "faucet_query",
    }
)

REQUIRED_READ_ONLY_TOOLS = frozenset(
    {
        "faucet_list_services",
        "faucet_list_tables",
        "faucet_describe_table",
        "faucet_query",
    }
)


class ToolPolicyError(ValueError):
    """Raised when the exposed MCP tools cannot satisfy the Agent policy."""


@dataclass(frozen=True)
class ToolPolicy:
    """Restrict an Agent to explicitly approved, read-only MCP tools."""

    allowed_names: frozenset[str] = READ_ONLY_TOOL_NAMES
    required_names: frozenset[str] = REQUIRED_READ_ONLY_TOOLS

    def filter_tools(self, tools: Iterable[Tool]) -> list[Tool]:
        filtered = [tool for tool in tools if tool.name in self.allowed_names]
        available = {tool.name for tool in filtered}
        missing = sorted(self.required_names - available)
        if missing:
            raise ToolPolicyError(
                "Faucet 未提供数据库 Agent 所需的只读工具：" + "、".join(missing)
            )
        return filtered

    def is_allowed(self, tool_name: str) -> bool:
        return tool_name in self.allowed_names


def to_openai_tool(tool: Tool) -> dict[str, Any]:
    """Convert an MCP tool declaration into a Chat Completions tool schema."""
    parameters = dict(tool.input_schema or {})
    parameters.setdefault("type", "object")
    parameters.setdefault("properties", {})

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or tool.title or "",
            "parameters": parameters,
        },
    }

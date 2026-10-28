from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import Any

import pytest
from mcp.types import Tool

from agent.mcp_client import MCPToolExecution
from agent.runtime import AgentStepLimitError, FaucetAgent


class FakeToolClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def list_tools(self) -> list[Tool]:
        definitions = {
            "faucet_list_services": {},
            "faucet_list_tables": {"service": {"type": "string"}},
            "faucet_describe_table": {
                "service": {"type": "string"},
                "table": {"type": "string"},
            },
            "faucet_query": {
                "service": {"type": "string"},
                "table": {"type": "string"},
            },
            "faucet_delete": {
                "service": {"type": "string"},
                "table": {"type": "string"},
            },
        }
        return [
            Tool(
                name=name,
                description=f"{name} description",
                inputSchema={
                    "type": "object",
                    "properties": properties,
                },
            )
            for name, properties in definitions.items()
        ]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> MCPToolExecution:
        self.calls.append((name, arguments))
        if name == "faucet_list_services":
            return MCPToolExecution(
                data=[{"name": "demo", "is_active": True}],
                is_error=False,
            )
        if name == "faucet_query":
            return MCPToolExecution(
                data=[{"count": 12}],
                is_error=False,
            )
        return MCPToolExecution(data=[], is_error=False)


class FakeModel:
    def __init__(self, messages: list[SimpleNamespace]) -> None:
        self._messages = messages
        self.requests: list[list[dict[str, Any]]] = []
        self.tool_names: list[set[str]] = []

    async def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> Any:
        self.requests.append([dict(message) for message in messages])
        self.tool_names.append(
            {tool["function"]["name"] for tool in tools}
        )
        message = self._messages.pop(0)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message)],
        )


def tool_call(
    call_id: str,
    name: str,
    arguments: dict[str, Any],
) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(
            name=name,
            arguments=json.dumps(arguments),
        ),
    )


def assistant_tool_message(*calls: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(
        content=None,
        tool_calls=list(calls),
    )


def final_message(content: str) -> SimpleNamespace:
    return SimpleNamespace(content=content, tool_calls=[])


def test_agent_executes_multi_step_read_only_flow() -> None:
    model = FakeModel(
        [
            assistant_tool_message(
                tool_call("call_1", "faucet_list_services", {}),
            ),
            assistant_tool_message(
                tool_call(
                    "call_2",
                    "faucet_query",
                    {"service": "demo", "table": "users"},
                ),
            ),
            final_message("users 表共有 12 条记录。"),
        ]
    )
    tool_client = FakeToolClient()

    result = asyncio.run(
        FaucetAgent(
            model=model,
            tool_client=tool_client,
            max_steps=4,
        ).run("演示库里的 users 表有多少条记录？")
    )

    assert result.answer == "users 表共有 12 条记录。"
    assert result.model_turns == 3
    assert [call[0] for call in tool_client.calls] == [
        "faucet_list_services",
        "faucet_query",
    ]
    assert all(
        "faucet_delete" not in names
        for names in model.tool_names
    )
    assert [trace.status for trace in result.tool_traces] == [
        "success",
        "success",
    ]

    final_request = model.requests[-1]
    assert final_request[-1]["role"] == "tool"
    assert json.loads(final_request[-1]["content"]) == [{"count": 12}]


def test_agent_rejects_hallucinated_mutation_tool() -> None:
    model = FakeModel(
        [
            assistant_tool_message(
                tool_call(
                    "call_1",
                    "faucet_delete",
                    {"service": "demo", "table": "users"},
                ),
            ),
            final_message("不能删除数据。"),
        ]
    )
    tool_client = FakeToolClient()

    result = asyncio.run(
        FaucetAgent(
            model=model,
            tool_client=tool_client,
            max_steps=2,
        ).run("删除 users 表")
    )

    assert result.answer == "不能删除数据。"
    assert tool_client.calls == []
    assert result.tool_traces[0].status == "denied"
    assert result.tool_traces[0].tool_name == "faucet_delete"


def test_agent_stops_after_step_limit() -> None:
    repeated_call = assistant_tool_message(
        tool_call("call_1", "faucet_list_services", {}),
    )
    model = FakeModel([repeated_call, repeated_call])
    agent = FaucetAgent(
        model=model,
        tool_client=FakeToolClient(),
        max_steps=2,
    )

    with pytest.raises(AgentStepLimitError):
        asyncio.run(agent.run("继续调用工具"))

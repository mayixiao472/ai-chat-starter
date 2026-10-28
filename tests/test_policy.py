from agent.policy import (
    READ_ONLY_TOOL_NAMES,
    ToolPolicy,
    to_openai_tool,
)
from mcp.types import Tool


def make_tool(name: str, description: str = "test tool") -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
            },
            "required": ["service"],
        },
    )


def test_policy_keeps_only_read_only_faucet_tools() -> None:
    tools = [
        make_tool(name)
        for name in (
            *sorted(READ_ONLY_TOOL_NAMES),
            "faucet_insert",
            "faucet_update",
            "faucet_delete",
            "faucet_raw_sql",
        )
    ]

    filtered = ToolPolicy().filter_tools(tools)

    assert {tool.name for tool in filtered} == READ_ONLY_TOOL_NAMES


def test_tool_schema_conversion_preserves_parameters() -> None:
    schema = to_openai_tool(make_tool("faucet_list_tables"))

    assert schema["type"] == "function"
    assert schema["function"]["name"] == "faucet_list_tables"
    assert schema["function"]["parameters"]["required"] == ["service"]


def test_unknown_tool_is_not_allowed() -> None:
    policy = ToolPolicy()

    assert policy.is_allowed("faucet_query")
    assert not policy.is_allowed("faucet_delete")
    assert not policy.is_allowed("unexpected_tool")

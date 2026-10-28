from types import SimpleNamespace

from agent.mcp_client import tool_result_payload


def test_structured_content_has_priority() -> None:
    result = SimpleNamespace(
        structured_content={"count": 3},
        content=[SimpleNamespace(text='{"count": 999}')],
    )

    assert tool_result_payload(result) == {"count": 3}


def test_text_json_is_parsed() -> None:
    result = SimpleNamespace(
        structured_content=None,
        content=[SimpleNamespace(text='[{"name": "demo"}]')],
    )

    assert tool_result_payload(result) == [{"name": "demo"}]


def test_plain_text_is_preserved() -> None:
    result = SimpleNamespace(
        structured_content=None,
        content=[SimpleNamespace(text="Forbidden")],
    )

    assert tool_result_payload(result) == "Forbidden"

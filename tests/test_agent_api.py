from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import agent.router as router_module
from agent.config import AgentConfigError
from agent.runtime import AgentRunResult
from agent.trace import AgentToolTrace


def build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router_module.router)
    return app


def test_database_agent_endpoint_returns_answer_and_trace(monkeypatch) -> None:
    async def fake_run(question: str, *, max_steps: int | None = None):
        assert question == "documents 表有多少条记录？"
        assert max_steps == 4
        return AgentRunResult(
            answer="documents 表有 2 条记录。",
            model_turns=3,
            tool_traces=[
                AgentToolTrace(
                    model_turn=2,
                    tool_call_id="call_1",
                    tool_name="faucet_query",
                    arguments={
                        "service": "ai_chat_starter",
                        "table": "documents",
                    },
                    status="success",
                    result={"records": [{"total": 2}]},
                    duration_ms=12.5,
                )
            ],
        )

    monkeypatch.setattr(router_module, "run_database_agent", fake_run)
    client = TestClient(build_test_app())

    response = client.post(
        "/db-agent/chat",
        json={
            "question": "documents 表有多少条记录？",
            "max_steps": 4,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "documents 表有 2 条记录。"
    assert payload["model_turns"] == 3
    assert payload["tool_calls"][0]["tool_name"] == "faucet_query"


def test_database_agent_endpoint_maps_missing_config(monkeypatch) -> None:
    async def fake_run(question: str, *, max_steps: int | None = None):
        raise AgentConfigError("FAUCET_API_KEY")

    monkeypatch.setattr(router_module, "run_database_agent", fake_run)
    client = TestClient(build_test_app())

    response = client.post(
        "/db-agent/chat",
        json={"question": "演示库里有哪些表？"},
    )

    assert response.status_code == 503
    assert "配置不完整" in response.json()["detail"]


def test_database_agent_endpoint_rejects_blank_question() -> None:
    client = TestClient(build_test_app())

    response = client.post(
        "/db-agent/chat",
        json={"question": "   "},
    )

    assert response.status_code == 400

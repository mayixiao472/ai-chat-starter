"""FastAPI route for the Faucet database Agent."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import AgentConfigError
from .runtime import AgentStepLimitError
from .service import run_database_agent


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/db-agent",
    tags=["database-agent"],
)


class DBAgentChatRequest(BaseModel):
    """A natural-language question for the read-only database Agent."""

    question: str = Field(min_length=1, max_length=2000)
    max_steps: int | None = Field(default=None, ge=1, le=12)


class DBAgentToolCall(BaseModel):
    """One model-requested MCP tool call."""

    model_turn: int
    tool_call_id: str
    tool_name: str
    arguments: dict[str, Any]
    status: str
    result: Any = None
    error: str | None = None
    duration_ms: float


class DBAgentChatResponse(BaseModel):
    """Answer plus the evidence needed to audit how it was produced."""

    answer: str
    model_turns: int
    tool_calls: list[DBAgentToolCall]


@router.post(
    "/chat",
    response_model=DBAgentChatResponse,
    summary="通过 Faucet MCP 询问数据库",
)
async def chat_with_database(request: DBAgentChatRequest) -> DBAgentChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question 不能为空。")

    try:
        result = await run_database_agent(
            question,
            max_steps=request.max_steps,
        )
    except AgentConfigError as error:
        raise HTTPException(
            status_code=503,
            detail=f"数据库 Agent 配置不完整：{error}",
        ) from error
    except AgentStepLimitError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except Exception as error:
        logger.exception("database agent request failed")
        raise HTTPException(
            status_code=502,
            detail=f"数据库 Agent 执行失败：{type(error).__name__}: {error}",
        ) from error

    return DBAgentChatResponse(**result.to_dict())

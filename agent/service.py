"""Shared service entry point for CLI and FastAPI callers."""

from __future__ import annotations

from dataclasses import replace

from .config import AgentConfig
from .mcp_client import open_faucet_session
from .runtime import AgentRunResult, FaucetAgent, build_openai_model


async def run_database_agent(
    question: str,
    *,
    max_steps: int | None = None,
    config: AgentConfig | None = None,
) -> AgentRunResult:
    """Run one single-turn, read-only database Agent request."""
    runtime_config = config or AgentConfig.from_env()
    if max_steps is not None:
        runtime_config = replace(runtime_config, max_steps=max_steps)

    async with open_faucet_session(runtime_config) as mcp_client:
        openai_client, model = build_openai_model(runtime_config)
        try:
            return await FaucetAgent(
                model=model,
                tool_client=mcp_client,
                max_steps=runtime_config.max_steps,
            ).run(question)
        finally:
            await openai_client.close()

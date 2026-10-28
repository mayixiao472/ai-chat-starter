"""Faucet MCP client used by the database Agent."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from mcp.types import Tool

from .config import AgentConfig


@dataclass(frozen=True)
class MCPToolExecution:
    data: Any
    is_error: bool


class FaucetMCPClient:
    """Thin async wrapper around an initialized MCP Client session."""

    def __init__(self, client: Client) -> None:
        self._client = client

    async def list_tools(self) -> list[Tool]:
        tools: list[Tool] = []
        cursor: str | None = None

        while True:
            result = await self._client.list_tools(cursor=cursor)
            tools.extend(result.tools)
            cursor = result.next_cursor
            if not cursor:
                return tools

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> MCPToolExecution:
        result = await self._client.call_tool(name, arguments)
        return MCPToolExecution(
            data=tool_result_payload(result),
            is_error=bool(result.is_error),
        )


def tool_result_payload(result: Any) -> Any:
    """Prefer structured MCP content, then parse Faucet's text JSON."""
    structured = getattr(result, "structured_content", None)
    if structured is None:
        structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured

    text_parts: list[str] = []
    for item in getattr(result, "content", []):
        text = getattr(item, "text", None)
        if isinstance(text, str):
            text_parts.append(text)

    text = "\n".join(text_parts).strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


@asynccontextmanager
async def open_faucet_session(
    config: AgentConfig,
) -> AsyncIterator[FaucetMCPClient]:
    """Open one authenticated Streamable HTTP MCP session."""
    timeout = httpx2.Timeout(
        connect=10.0,
        read=config.read_timeout_seconds,
        write=10.0,
        pool=10.0,
    )
    async with httpx2.AsyncClient(
        headers={"X-API-Key": config.faucet_api_key},
        timeout=timeout,
    ) as http_client:
        transport = streamable_http_client(
            config.mcp_url,
            http_client=http_client,
        )
        async with Client(
            transport,
            read_timeout_seconds=config.read_timeout_seconds,
        ) as client:
            yield FaucetMCPClient(client)

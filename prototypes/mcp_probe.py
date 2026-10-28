"""Probe a Faucet MCP server over Streamable HTTP.

This script intentionally does not call an LLM. It verifies the transport,
authentication, MCP initialization, tool discovery, and the two read-only
tool calls needed by the future database Agent.

Required environment variables:
    FAUCET_MCP_URL  Defaults to http://localhost:8080/mcp
    FAUCET_API_KEY  A read-only Faucet API key; never commit this value

Example:
    python prototypes/mcp_probe.py
    python prototypes/mcp_probe.py --service demo
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    import httpx2
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client
except ImportError as error:
    raise SystemExit(
        "缺少 MCP 依赖。请先运行：\n"
        '  python -m pip install "mcp>=2.3.0,<3"\n'
        f"\n原始错误：{error}"
    ) from error


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MCP_URL = "http://localhost:8080/mcp"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="验证 Faucet MCP 的 Streamable HTTP 连接与只读工具调用。",
    )
    parser.add_argument(
        "--url",
        default=os.getenv("FAUCET_MCP_URL", DEFAULT_MCP_URL),
        help="Faucet MCP 地址，默认读取 FAUCET_MCP_URL",
    )
    parser.add_argument(
        "--service",
        default="",
        help="传给 faucet_list_tables 的服务名；省略时使用第一个可用服务",
    )
    parser.add_argument(
        "--read-timeout",
        type=float,
        default=60.0,
        help="单次 MCP 请求的读取超时秒数，默认 60",
    )
    return parser.parse_args()


def tool_result_payload(result: Any) -> Any:
    """Prefer structured content, then try to parse Faucet's JSON text."""
    structured = getattr(result, "structured_content", None)
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


def choose_service(services: Any) -> str:
    """Return the first active service exposed by faucet_list_services."""
    if not isinstance(services, list):
        return ""

    for service in services:
        if not isinstance(service, dict):
            continue
        name = service.get("name")
        if isinstance(name, str) and name and service.get("is_active", True):
            return name
    return ""


async def list_all_tools(client: Client) -> list[Any]:
    """Follow MCP pagination instead of assuming all tools fit on one page."""
    tools: list[Any] = []
    cursor: str | None = None

    while True:
        result = await client.list_tools(cursor=cursor)
        tools.extend(result.tools)
        cursor = getattr(result, "next_cursor", None)
        if not cursor:
            return tools


async def call_tool(client: Client, name: str, arguments: dict[str, Any]) -> Any:
    """Call a tool and fail clearly when Faucet returns a tool-level error."""
    result = await client.call_tool(name, arguments)
    if getattr(result, "is_error", False):
        payload = tool_result_payload(result)
        raise RuntimeError(f"{name} 返回错误：{payload or '未提供错误内容'}")
    return tool_result_payload(result)


async def probe(url: str, api_key: str, requested_service: str, read_timeout: float) -> None:
    timeout = httpx2.Timeout(connect=10.0, read=read_timeout, write=10.0, pool=10.0)

    async with httpx2.AsyncClient(
        headers={"X-API-Key": api_key},
        timeout=timeout,
    ) as http_client:
        transport = streamable_http_client(url, http_client=http_client)

        # Entering Client performs the MCP initialize handshake. The negotiated
        # server and protocol information are available immediately afterwards.
        async with Client(transport) as client:
            server_info = getattr(client, "server_info", None)
            protocol_version = getattr(client, "protocol_version", None)
            print("MCP 初始化成功")
            print(f"  server: {server_info or 'unknown'}")
            print(f"  protocol: {protocol_version or 'unknown'}")

            tools = await list_all_tools(client)
            print(f"\n可用工具（{len(tools)} 个）")
            for tool in tools:
                description = (getattr(tool, "description", "") or "").strip()
                first_line = description.splitlines()[0] if description else "无描述"
                print(f"  - {tool.name}: {first_line}")

            tool_names = {tool.name for tool in tools}
            required_tools = {"faucet_list_services", "faucet_list_tables"}
            missing_tools = required_tools - tool_names
            if missing_tools:
                missing = ", ".join(sorted(missing_tools))
                raise RuntimeError(f"缺少探测所需工具：{missing}")

            print("\n调用 faucet_list_services")
            services = await call_tool(client, "faucet_list_services", {})
            print(json.dumps(services, ensure_ascii=False, indent=2))

            service_name = requested_service.strip() or choose_service(services)
            if not service_name:
                raise RuntimeError(
                    "faucet_list_services 没有返回可用服务。"
                    "请先在 Faucet 中添加数据库，或使用 --service 指定服务名。"
                )

            print(f"\n调用 faucet_list_tables（service={service_name}）")
            tables = await call_tool(
                client,
                "faucet_list_tables",
                {"service": service_name},
            )
            print(json.dumps(tables, ensure_ascii=False, indent=2))


def main() -> int:
    load_dotenv(PROJECT_DIR / ".env", override=False)
    args = parse_args()
    url = args.url.strip()
    api_key = (os.getenv("FAUCET_API_KEY") or "").strip()

    if not url:
        print("错误：Faucet MCP 地址为空。", file=sys.stderr)
        return 2
    if not api_key:
        print(
            "错误：没有找到 FAUCET_API_KEY。\n"
            "请在本项目 .env 中配置一个只读 API Key，例如：\n"
            "  FAUCET_MCP_URL=http://localhost:8080/mcp\n"
            "  FAUCET_API_KEY=faucet_xxx",
            file=sys.stderr,
        )
        return 2

    print(f"连接 Faucet MCP：{url}")
    print("鉴权方式：X-API-Key（值已隐藏）")

    try:
        asyncio.run(
            probe(
                url=url,
                api_key=api_key,
                requested_service=args.service,
                read_timeout=args.read_timeout,
            )
        )
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130
    except Exception as error:
        print(f"\n探测失败：{type(error).__name__}: {error}", file=sys.stderr)
        message = str(error).lower()
        if "401" in message or "unauthorized" in message or "forbidden" in message:
            print(
                "提示：检查 FAUCET_API_KEY 是否正确、是否已撤销，"
                "以及角色是否具有 GET 权限。",
                file=sys.stderr,
            )
        elif "connect" in message or "refused" in message:
            print(
                "提示：确认 Faucet 已启动，并检查 FAUCET_MCP_URL 是否为 /mcp 地址。",
                file=sys.stderr,
            )
        return 1

    print("\n探测完成：连接、初始化、工具发现和只读工具调用均成功。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

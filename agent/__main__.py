"""CLI entry point for the read-only Faucet database Agent."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .config import AgentConfig, AgentConfigError
from .runtime import AgentStepLimitError
from .service import run_database_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="通过 Faucet MCP 执行只读数据库问答。",
    )
    parser.add_argument(
        "question",
        nargs="?",
        default="",
        help="要询问数据库的问题；省略时进入交互输入",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=0,
        help="覆盖 AGENT_MAX_STEPS",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出完整 JSON，包含工具调用轨迹",
    )
    return parser.parse_args()


async def run_agent(config: AgentConfig, question: str) -> dict[str, object]:
    result = await run_database_agent(
        question,
        config=config,
    )
    return result.to_dict()


def main() -> int:
    args = parse_args()
    try:
        config = AgentConfig.from_env()
        if args.max_steps:
            from dataclasses import replace

            config = replace(config, max_steps=args.max_steps)
    except AgentConfigError as error:
        print(f"配置错误：{error}", file=sys.stderr)
        return 2

    question = args.question.strip()
    if not question:
        try:
            question = input("问数据库：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已取消。", file=sys.stderr)
            return 130
    if not question:
        print("问题不能为空。", file=sys.stderr)
        return 2

    try:
        result = asyncio.run(run_agent(config, question))
    except AgentStepLimitError as error:
        print(f"Agent 停止：{error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130
    except Exception as error:
        print(f"运行失败：{type(error).__name__}: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0

    print("\n回答：")
    print(result["answer"])
    tool_calls = result.get("tool_calls", [])
    if tool_calls:
        print("\n工具调用：")
        for call in tool_calls:
            print(
                f"- 第 {call['model_turn']} 回合：{call['tool_name']} "
                f"[{call['status']}] {call['duration_ms']:.1f} ms"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Configuration for the Faucet database Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[1]


class AgentConfigError(ValueError):
    """Raised when required Agent configuration is missing or invalid."""


def _read_positive_int(name: str, default: int) -> int:
    raw_value = (os.getenv(name) or "").strip()
    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError as error:
        raise AgentConfigError(f"{name} 必须是整数。") from error

    if value < 1:
        raise AgentConfigError(f"{name} 必须大于 0。")
    return value


@dataclass(frozen=True)
class AgentConfig:
    """Runtime settings loaded from the project's .env file."""

    mcp_url: str
    faucet_api_key: str
    model_api_key: str
    model_name: str
    model_base_url: str | None
    max_steps: int = 6
    read_timeout_seconds: float = 60.0

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "AgentConfig":
        load_dotenv(env_file or PROJECT_DIR / ".env", override=False)

        mcp_url = (os.getenv("FAUCET_MCP_URL") or "").strip()
        faucet_api_key = (os.getenv("FAUCET_API_KEY") or "").strip()
        model_api_key = (
            os.getenv("DEEPSEEK_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        ).strip()
        model_name = (os.getenv("OPENAI_MODEL") or "deepseek-v4-flash").strip()
        model_base_url = (os.getenv("OPENAI_BASE_URL") or "").strip() or None

        missing: list[str] = []
        if not mcp_url:
            missing.append("FAUCET_MCP_URL")
        if not faucet_api_key or faucet_api_key.startswith("faucet_your_"):
            missing.append("FAUCET_API_KEY")
        if not model_api_key or model_api_key.startswith("your_"):
            missing.append("DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
        if missing:
            raise AgentConfigError(
                "缺少必要配置：" + "、".join(missing)
            )

        return cls(
            mcp_url=mcp_url,
            faucet_api_key=faucet_api_key,
            model_api_key=model_api_key,
            model_name=model_name,
            model_base_url=model_base_url,
            max_steps=_read_positive_int("AGENT_MAX_STEPS", 6),
        )

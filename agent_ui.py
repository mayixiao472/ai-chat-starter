"""Streamlit page for testing the read-only Faucet database Agent."""

from __future__ import annotations

import json
import os

import httpx2
import streamlit as st
from dotenv import load_dotenv


load_dotenv(override=False)

DEFAULT_API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Faucet 数据库 Agent",
    page_icon="DB",
    layout="wide",
)

if "database_agent_history" not in st.session_state:
    st.session_state.database_agent_history = []


def ask_database_agent(
    api_url: str,
    question: str,
    max_steps: int,
) -> dict[str, object]:
    response = httpx2.post(
        f"{api_url.rstrip('/')}/db-agent/chat",
        json={
            "question": question,
            "max_steps": max_steps,
        },
        timeout=httpx2.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0),
    )
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {"detail": response.text}

    if response.is_error:
        detail = payload.get("detail") if isinstance(payload, dict) else payload
        raise RuntimeError(f"HTTP {response.status_code}: {detail}")

    if not isinstance(payload, dict):
        raise RuntimeError("数据库 Agent 返回了非对象 JSON。")
    return payload


def render_history() -> None:
    for item in st.session_state.database_agent_history:
        with st.chat_message("user"):
            st.write(item["question"])
        with st.chat_message("assistant"):
            st.write(item["answer"])
            tool_calls = item.get("tool_calls", [])
            if tool_calls:
                with st.expander(f"查看工具调用轨迹（{len(tool_calls)} 次）"):
                    st.json(tool_calls)


st.title("Faucet 数据库 Agent")
st.caption(
    "通过 FastAPI 调用 MCP Agent。默认只暴露服务发现、表结构读取和查询工具，"
    "不会执行插入、更新、删除或原始 SQL。"
)

with st.sidebar:
    st.header("连接设置")
    api_url = st.text_input(
        "FastAPI 地址",
        value=os.getenv("AGENT_API_BASE_URL", DEFAULT_API_URL),
    )
    max_steps = st.slider(
        "最大模型回合数",
        min_value=1,
        max_value=12,
        value=6,
    )
    if st.button("清空当前对话", use_container_width=True):
        st.session_state.database_agent_history = []
        st.rerun()

render_history()

question = st.chat_input("询问演示数据库，例如：documents 表有多少条记录？")
if question:
    question = question.strip()
    if not question:
        st.warning("问题不能为空。")
    else:
        with st.chat_message("user"):
            st.write(question)

        try:
            with st.spinner("Agent 正在发现数据库、选择工具并组织回答..."):
                result = ask_database_agent(
                    api_url=api_url,
                    question=question,
                    max_steps=max_steps,
                )
        except Exception as error:
            with st.chat_message("assistant"):
                st.error(f"查询失败：{error}")
                st.caption("请检查 Faucet、FastAPI 和模型 API 是否都在运行。")
        else:
            answer = str(result.get("answer") or "")
            history_item = {
                "question": question,
                "answer": answer,
                "tool_calls": result.get("tool_calls", []),
            }
            st.session_state.database_agent_history.append(history_item)
            with st.chat_message("assistant"):
                st.write(answer)
                tool_calls = history_item["tool_calls"]
                if tool_calls:
                    with st.expander(f"查看工具调用轨迹（{len(tool_calls)} 次）"):
                        st.json(tool_calls)

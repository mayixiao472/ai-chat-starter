# Faucet Database Agent

第二阶段在原有 RAG 服务之外新增一个只读数据库 Agent。它不绕过 Faucet，
而是作为 MCP 客户端调用 Faucet 暴露的结构化工具。

## 执行链路

```text
用户问题
-> Python Agent
-> 获取 Faucet MCP 工具
-> 筛选只读工具
-> 模型选择工具
-> Faucet 执行查询
-> 工具结果返回模型
-> 模型生成最终回答
```

## 安全边界

Agent 只向模型暴露以下工具：

- `faucet_list_services`
- `faucet_list_tables`
- `faucet_describe_table`
- `faucet_query`

插入、更新、删除和原始 SQL 工具不会进入模型的工具列表。即使模型虚构了
这些工具名，运行时也会拒绝执行。Faucet 端的 API Key 仍应绑定只读角色，
形成客户端白名单与服务端 RBAC 两层保护。

## 配置

在 `.env` 中配置：

```text
FAUCET_MCP_URL=http://localhost:8080/mcp
FAUCET_API_KEY=faucet_your_read_only_key_here
AGENT_MAX_STEPS=6
```

模型继续使用现有的 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`、
`OPENAI_BASE_URL` 和 `OPENAI_MODEL`。

## 运行

先启动 FastAPI：

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

再启动 Streamlit 数据库 Agent 页面：

```powershell
.\.venv\Scripts\python.exe -m streamlit run agent_ui.py
```

浏览器页面会调用：

```text
POST http://127.0.0.1:8000/db-agent/chat
```

也可以在 Swagger 的 `database-agent` 分组中直接测试该接口：

```text
http://127.0.0.1:8000/docs
```

命令行入口仍然可用：

```powershell
.\.venv\Scripts\python.exe -m agent "演示库里有哪些表？"
```

输出工具轨迹：

```powershell
.\.venv\Scripts\python.exe -m agent --json "演示库里有哪些表？"
```

覆盖最大模型回合数：

```powershell
.\.venv\Scripts\python.exe -m agent --max-steps 4 "演示库里有哪些表？"
```

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest
```

测试使用假模型和假 MCP 工具，不请求真实 API，也不访问数据库。

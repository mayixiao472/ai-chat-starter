# AI Chat Starter

这是一个面向 AI 后端开发学习的文档问答项目。

项目目标不是做一个复杂的聊天机器人，而是完整跑通一条 AI 应用开发链路：

```text
用户上传文档
-> 后端切分文本
-> 生成 embedding
-> 写入 Chroma 向量库
-> MySQL 保存文档记录
-> 用户提问
-> 检索相关 chunks
-> 调用大模型生成回答
-> 返回回答和引用来源
```

## 技术栈

```text
Python
FastAPI
Pydantic
OpenAI 兼容 SDK
Chroma
MySQL
Streamlit
Docker
```

## 项目结构

```text
ai-chat-starter/
  api.py                 FastAPI 后端接口
  main.py                LLM、embedding、RAG、Chroma 核心逻辑
  database.py            MySQL 连接和文档记录 CRUD
  app.py                 Streamlit 演示页面
  api_tests.http         接口测试用例
  mysql_schema.sql       MySQL 建表脚本
  Dockerfile             Docker 启动配置
  requirements.txt       Python 依赖
  .env.example           环境变量示例
  docs/
    architecture.md      项目架构和数据流说明
```

## 核心功能

- 文档上传：支持上传 `.txt` 文件。
- 文本切分：把长文档切成多个 chunks。
- 向量检索：使用 Chroma 保存 chunk embedding，并按相似度检索。
- RAG 问答：把检索到的 chunks 作为上下文交给大模型回答。
- 引用来源：回答时返回使用到的 chunks。
- 文档管理：使用 MySQL 保存文档元数据。
- RESTful API：提供文档上传、文档列表、文档问答、删除文档等接口。
- Docker 启动：支持用容器运行 FastAPI 服务。

## 环境变量

先复制示例文件：

```powershell
Copy-Item .env.example .env
```

然后在 `.env` 中填写你的真实配置。

常见配置包括：

```text
OPENAI_API_KEY=你的聊天模型 API key
OPENAI_BASE_URL=你的聊天模型接口地址
OPENAI_MODEL=你的聊天模型名称

EMBEDDING_API_KEY=你的 embedding API key
EMBEDDING_BASE_URL=你的 embedding 接口地址
EMBEDDING_MODEL=你的 embedding 模型名称

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的 MySQL 密码
MYSQL_DATABASE=ai_chat_starter
```

不要把 `.env` 上传到 GitHub，因为里面有私密 key 和数据库密码。

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 初始化 MySQL

先确认 MySQL 服务已经启动。

然后进入项目目录，执行建表脚本：

```powershell
mysql -u root -p
```

进入 MySQL 后执行：

```sql
source mysql_schema.sql;
```

如果你在 PowerShell 里直接执行 SQL 文件，需要注意 PowerShell 不支持 Linux 风格的 `<` 重定向。

## 启动 FastAPI

```powershell
python -m uvicorn api:app --reload
```

启动后打开：

```text
http://127.0.0.1:8000/docs
```

这里可以直接测试所有接口。

## 主要接口

### 健康检查

```text
GET /health
```

作用：确认后端服务是否正常启动。

### 聊天

```text
POST /chat
```

请求示例：

```json
{
  "question": "什么是 RAG？"
}
```

### 文本总结

```text
POST /summarize
```

请求示例：

```json
{
  "text": "这里放一段需要总结的文本。"
}
```

### 上传文档

```text
POST /documents
```

作用：上传 `.txt` 文件，后端切分文本并写入 Chroma，同时把文档记录写入 MySQL。

返回示例：

```json
{
  "id": 1,
  "filename": "example.txt",
  "collection_name": "example",
  "chunk_count": 12,
  "indexed_count": 12
}
```

### 查询文档列表

```text
GET /documents
```

作用：从 MySQL 查询已经上传过的文档记录。

### 根据文档提问

```text
POST /documents/{document_id}/questions
```

请求示例：

```json
{
  "question": "这篇文档主要讲了什么？",
  "top_k": 3,
  "min_score": 0.2
}
```

后端流程：

```text
document_id
-> 查询 MySQL 得到 collection_name
-> 查询 Chroma 得到相关 chunks
-> 调用 LLM
-> 返回 answer 和 sources
```

### 删除文档

```text
DELETE /documents/{document_id}
```

作用：删除 MySQL 文档记录，并删除对应的 Chroma collection。

## Docker 启动

构建镜像：

```powershell
docker build -t ai-chat-starter-api .
```

运行容器：

```powershell
docker run --env-file .env -p 8000:8000 ai-chat-starter-api
```

然后打开：

```text
http://127.0.0.1:8000/docs
```

如果容器里的 FastAPI 需要访问你电脑本机的 MySQL，`MYSQL_HOST` 可能需要设置成：

```text
MYSQL_HOST=host.docker.internal
```

## 项目架构

更完整的架构说明见：

```text
docs/architecture.md
```

简化版：

```text
用户 / 前端 / API 文档
-> FastAPI 接口层
-> main.py 核心逻辑层
-> Chroma 向量库
-> MySQL 业务记录
-> LLM / Embedding API
```

## 项目亮点

- 手写 RAG 主流程，而不是一开始依赖 LangChain。
- 区分了 Chroma 和 MySQL 的职责。
- 提供 RESTful API，项目形态更接近真实后端服务。
- 接口返回引用来源，便于解释回答依据。
- 支持 Docker 启动，降低环境不一致问题。

## 后续优化方向

- 增加用户登录和简单权限校验。
- 增加 Redis 缓存或限流。
- 增加流式输出。
- 增加异步任务处理文档 embedding。
- 使用 Docker Compose 同时启动 FastAPI、MySQL 和 Redis。
- 增加更完整的单元测试和接口测试。
- 接入 LangChain，对比框架 RAG 和手写 RAG 的区别。

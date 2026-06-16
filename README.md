# ai-chat-starter

这是你的第一个最小 AI 应用项目。

现在的目标不是做一个很复杂、很漂亮的聊天机器人，而是先理解 AI 应用开发最核心的一条流程：

```text
用户问题 -> prompt/messages -> 调用大模型 API -> 得到回答
```

## 你会学到什么

- API key 是什么
- 为什么密钥要放在 `.env` 文件里
- `requirements.txt` 是做什么用的
- `role` 和 `content` 如何组成一条消息
- Python 脚本如何向大模型发送请求
- Streamlit 如何把 AI 调用做成网页
- `.txt` 文件如何被读取并交给模型总结

## 一个月学习路线

完整路线放在 [LEARNING_PLAN.md](./LEARNING_PLAN.md)。

这个项目目前对应第 1 周：LLM API 基础 + Streamlit。你先把这里的主流程读懂，再进入 RAG、FastAPI、数据库和 Docker。

## 项目结构

```text
ai-chat-starter/
  main.py
  app.py
  api.py
  database.py
  mysql_schema.sql
  requirements.txt
  .env.example
  LEARNING_PLAN.md
  notes/
    day01_minimal_llm_app.md
    day02_chat_history.md
    day03_streamlit_app.md
    day04_text_splitting.md
    day05_simple_retrieval.md
    day06_embedding_similarity.md
    day07_real_embedding_api.md
    day08_real_embedding_retrieval.md
    day09_vector_index_cache.md
    day10_chroma_vector_database.md
    day11_complete_rag.md
    day12_rag_quality_control.md
    day13_fastapi_restful_api.md
    day14_fastapi_chat_api.md
    day15_fastapi_summarize_api.md
    day16_fastapi_document_upload.md
    day17_fastapi_rag_api.md
    day18_mysql_basics.md
    day19_fastapi_mysql.md
```

## 环境准备

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

创建你本地的 `.env` 文件：

```powershell
Copy-Item .env.example .env
```

然后打开 `.env`，填入你自己的 API key。

如果你使用的是兼容 OpenAI 格式的其他平台，还需要在 `.env` 里配置：

```text
OPENAI_BASE_URL=你的平台接口地址
OPENAI_MODEL=你的平台模型名
```

如果你使用 OpenAI 官方接口，不需要配置 `OPENAI_BASE_URL`。

## 运行

如果你已经有 DeepSeek API key，使用真实 API 模式：

```text
AI_CHAT_MODE=real
```

如果你暂时没有 API key，可以使用 mock 模式：

```text
AI_CHAT_MODE=mock
```

mock 模式是假回答模式，不会请求真实 API，不消耗额度。它适合你先学习程序结构。

方式一：交互输入问题。

```powershell
python main.py
```

输入一个问题，按回车，然后等待模型回答。

方式二：直接在命令里传入问题。

```powershell
python main.py --question "用三句话解释什么是 AI 应用开发"
```

如果你在某些 IDE、自动运行环境或非交互终端里运行，程序可能无法等待你输入内容。这个时候就用第二种方式。

方式三：运行网页版本。

```powershell
python -m streamlit run app.py
```

然后浏览器会打开一个本地网页。你可以在网页里聊天，也可以上传 `.txt` 文件，让 AI 总结文本内容。

方式四：运行 FastAPI 后端。

```powershell
python -m uvicorn api:app --reload
```

然后打开：

```text
http://127.0.0.1:8000/docs
```

这里可以测试 `GET /health`、`POST /echo`、`POST /chat`、`POST /summarize`、`POST /documents`、`GET /documents` 和 `POST /ask-doc`。

## 使用 DeepSeek API

DeepSeek 官方 API 兼容 OpenAI SDK，所以这个项目仍然使用 `openai` 这个 Python 包，只是把接口地址和模型名换成 DeepSeek。

在 `.env` 里配置：

```text
DEEPSEEK_API_KEY=你的DeepSeek API key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
AI_CHAT_MODE=real
```

如果想用更强但可能更贵/更慢的模型，可以改成：

```text
OPENAI_MODEL=deepseek-v4-pro
```

官方文档入口：<https://api-docs.deepseek.com/zh-cn/>

## 这次为什么支持 `--question`

最开始的代码只有这一种输入方式：

```python
question = input("你: ").strip()
```

它适合普通终端，但不适合所有运行环境。有些环境不会真的等待你键盘输入，于是 Python 会报 `EOFError`。

现在程序支持：

- `python main.py`：手动输入问题
- `python main.py --question "你的问题"`：直接传入问题

这样程序更稳定，也更方便后面写测试和扩展功能。

## 如果还是报错，怎么看

现在程序会把常见错误翻译成中文：

- 认证失败：通常是 API key 错了
- 请求被限制：通常是额度、余额或频率限制
- 请求参数有问题：通常是模型名不对
- 网络连接失败：通常是连不上 API，或需要配置 `OPENAI_BASE_URL`

如果你看到“原始错误信息”，先不要慌。那说明 Python 代码已经跑起来了，问题发生在真实请求大模型 API 的阶段。

## 重要提醒

不要把 `.env` 上传到 GitHub。它里面有你的私人 API key。

这个项目已经进入第二阶段：在原有 Streamlit 演示页面之外，开始加入 FastAPI 后端接口、MySQL 文档记录和 RAG API。

# 一个月 AI 开发实习学习计划

这份计划服务于一个目标：一个月后，你不只是“跑通了几个项目”，而是能讲清楚 AI 应用从用户输入到模型回答的完整流程。

你的主线是：

```text
Python 工程基础
-> LLM API 应用
-> Streamlit / FastAPI
-> RAG
-> Git / Docker / Linux / SQL 基础
-> Agent / MCP / Ollama 作为加分项
```

每天建议学习 6 小时：

```text
1 小时：补基础知识
2 小时：读代码和理解逻辑
2 小时：项目实现或修改
1 小时：写笔记、README、面试表达
```

## 第 1 周：LLM 应用基础 + Streamlit

目标：能讲清楚“用户输入如何变成模型回答”。

重点学习：

- Python 项目结构
- 虚拟环境
- `requirements.txt`
- `.env`
- API key
- base URL
- model 参数
- `messages`
- `system` / `user` / `assistant`
- Streamlit 页面
- Git 基础

项目任务：

- 读懂 `main.py`
- 读懂 `app.py`
- 跑通命令行聊天
- 跑通网页聊天
- 跑通 `.txt` 文件总结
- 写清楚 README 运行步骤
- 做一次 Git 提交

你需要能回答：

- 为什么 API key 不能写进代码？
- 为什么 DeepSeek 也可以用 `openai` 这个 Python 包？
- `messages` 为什么是一个列表？
- 为什么历史对话会越变越长？
- 为什么 `app.py` 不能直接点运行，而要用 `streamlit run app.py`？
- 文件上传后，程序拿到的是文本还是 bytes？

## 第 2 周：RAG 文档问答

目标：完成一个标准 AI 应用实习项目。

重点学习：

- 文本读取
- 文本切分
- embedding
- 向量库
- 相似度检索
- Prompt 拼接
- 引用来源
- 无关问题处理

项目任务：

- 新建 RAG 文档问答项目
- 支持上传 `.txt` 或 `.md`
- 把文档切成小段
- 把问题和文档片段匹配起来
- 让模型基于相关片段回答
- 回答时显示引用片段
- 文档里没有答案时说明不知道

你需要能回答：

- RAG 为什么不能直接把整篇文档都塞给模型？
- embedding 是什么？
- 向量库解决了什么问题？
- 检索结果为什么要放进 prompt？
- RAG 和普通聊天机器人有什么区别？

## 第 3 周：FastAPI + RESTful API + SQL 基础

目标：把网页 Demo 升级成更像真实项目的后端服务。

重点学习：

- RESTful API
- `GET`
- `POST`
- JSON
- 状态码
- FastAPI
- Pydantic
- MySQL / SQL 基础
- 聊天记录或文档记录保存

项目任务：

- 写一个 `/chat` 接口
- 写一个 `/summarize` 接口
- 写一个 `/ask-doc` 接口
- 让 Streamlit 调用 FastAPI 后端
- 用 SQL 保存简单聊天记录或文档记录

你需要能回答：

- 前端、后端、模型 API 分别负责什么？
- `GET` 和 `POST` 有什么区别？
- 为什么接口通常返回 JSON？
- FastAPI 中请求体和响应体是什么？
- 数据库在 AI 应用里通常保存什么？

## 第 4 周：Docker + Linux + Agent 加分项 + 简历

目标：项目能展示，技术能讲，简历能写。

重点学习：

- Linux 常用命令
- Docker 基础
- `Dockerfile`
- 容器端口映射
- 简单工具调用
- Ollama
- MCP
- README
- 架构图
- 简历项目描述

项目任务：

- 用 Docker 跑 FastAPI 项目
- 做一个简单工具调用功能
- 半天体验 Ollama
- 半天了解 MCP 是什么
- 整理 GitHub README
- 准备项目截图
- 准备简历项目描述
- 准备面试讲解稿

你需要能回答：

- Docker 解决了什么问题？
- Linux 命令在部署和排错里有什么用？
- 工具调用和普通对话有什么区别？
- Ollama 和 API 调用有什么区别？
- MCP 大概想解决什么问题？
- 你的项目难点是什么？
- 你的项目还能怎么改进？

## 技术优先级

必须掌握：

```text
Python
LLM API
Prompt/messages
Streamlit
FastAPI
RESTful API
RAG
Git
README
```

需要基础掌握：

```text
MySQL
Docker
Linux
Chroma/FAISS
异常处理
日志
```

了解即可：

```text
Redis
Ollama
MCP
Agent
LangChain/LlamaIndex
```

暂时不要深入：

```text
多 Agent 系统
复杂 Agent-team
模型训练
SFT-Net 深改
Kubernetes
复杂数据库优化
```

## 每周验收标准

第 1 周结束：

- 能独立运行 `main.py`
- 能独立运行 `app.py`
- 能解释 `.env`、API key、messages
- 能用自己的话讲清楚最小 AI 应用流程

第 2 周结束：

- 有一个能运行的 RAG 文档问答项目
- 能显示引用来源
- 能处理无关问题
- README 能让别人复现运行

第 3 周结束：

- 有 FastAPI 后端接口
- 能用 Postman、浏览器或 Python 请求接口
- 能说明 RESTful API 的基本概念
- 能保存简单数据

第 4 周结束：

- 项目 README 完整
- 有项目架构图
- 有简历项目描述
- 有面试讲解稿
- 能讲清楚项目架构、难点和改进方向

## 学习原则

不要追求“我能背出所有概念”，要追求：

```text
我知道这段代码为什么存在。
我知道数据从哪里来，往哪里去。
我知道报错时该从哪里查。
我能把项目讲给面试官听。
```


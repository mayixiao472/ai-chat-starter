# Day 14：聊天接口 POST /chat

今天的目标是把第一阶段的聊天能力包装成 FastAPI 接口。

之前聊天流程是：

```text
命令行 / Streamlit
-> 调用 ask_llm
-> 显示回答
```

今天变成：

```text
前端 / 其他程序
-> POST /chat
-> FastAPI 调用 ask_llm
-> 返回 JSON
```

## 1. 今天新增了什么

在 `api.py` 里新增：

```text
POST /chat
```

请求体：

```json
{
  "question": "什么是 FastAPI？"
}
```

响应体：

```json
{
  "answer": "..."
}
```

## 2. ChatRequest 是什么

```python
class ChatRequest(BaseModel):
    question: str
```

它规定调用 `/chat` 时必须传：

```text
question 字段
并且 question 必须是字符串
```

这就是请求体模型。

## 3. ChatResponse 是什么

```python
class ChatResponse(BaseModel):
    answer: str
```

它规定 `/chat` 返回：

```text
answer 字段
并且 answer 是字符串
```

这就是响应体模型。

## 4. /chat 内部流程

代码逻辑是：

```text
1. 取出 request.question
2. 去掉前后空格
3. 如果问题为空，返回 400
4. 创建初始 messages
5. 把用户问题加入 messages
6. 调用 ask_llm(messages)
7. 返回 answer
```

## 5. 为什么空问题返回 400

400 表示：

```text
客户端请求有问题
```

如果用户传：

```json
{
  "question": ""
}
```

这不是服务器坏了，而是请求参数不合理，所以返回 400。

## 6. 为什么 API 报错返回 500

如果调用模型时出错，比如：

```text
API key 错误
余额不足
网络失败
模型名错误
```

这些发生在后端处理过程中，所以现在统一返回 500。

后面项目更成熟时，可以继续细分错误码。

## 7. 现在的 /chat 是单轮还是多轮

现在是单轮。

也就是说：

```text
每次请求只包含当前 question
```

它不会自动记住上一轮对话。

多轮聊天需要额外设计：

```text
conversation_id
历史 messages 存储
上下文长度控制
```

这会在后面数据库或会话管理阶段再学。

## 8. 今天怎么测试

启动：

```powershell
python -m uvicorn api:app --reload
```

打开：

```text
http://127.0.0.1:8000/docs
```

找到：

```text
POST /chat
```

点击 `Try it out`，输入：

```json
{
  "question": "用三句话解释什么是 FastAPI"
}
```

然后点击 `Execute`。

## 9. 今天你要能讲清楚

1. `/chat` 为什么用 POST？
2. `ChatRequest` 的作用是什么？
3. `ChatResponse` 的作用是什么？
4. `/chat` 是怎么复用 `main.py` 的？
5. 为什么空问题返回 400？
6. 现在的 `/chat` 为什么还不是多轮聊天？


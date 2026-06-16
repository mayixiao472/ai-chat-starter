# Day 15：文本总结接口 POST /summarize

今天的目标是把第一阶段的文本总结能力包装成 FastAPI 接口。

之前文本总结流程是：

```text
Streamlit 上传 txt
-> 读取文本
-> 调用 summarize_text
-> 页面显示总结
```

今天变成：

```text
前端 / 其他程序
-> POST /summarize
-> FastAPI 调用 summarize_text
-> 返回 JSON
```

## 1. 今天新增了什么

在 `api.py` 里新增：

```text
POST /summarize
```

请求体：

```json
{
  "text": "这里是一段需要总结的文本..."
}
```

响应体：

```json
{
  "summary": "..."
}
```

## 2. SummarizeRequest 是什么

```python
class SummarizeRequest(BaseModel):
    text: str
```

它规定调用 `/summarize` 时必须传：

```text
text 字段
并且 text 必须是字符串
```

## 3. SummarizeResponse 是什么

```python
class SummarizeResponse(BaseModel):
    summary: str
```

它规定 `/summarize` 返回：

```text
summary 字段
并且 summary 是字符串
```

## 4. /summarize 内部流程

代码逻辑是：

```text
1. 取出 request.text
2. 去掉前后空格
3. 如果文本为空，返回 400
4. 调用 summarize_text(text)
5. 返回 summary
```

## 5. /chat 和 /summarize 的区别

`/chat`：

```text
输入 question
输出 answer
适合普通问答
```

`/summarize`：

```text
输入 text
输出 summary
适合文本总结
```

它们都会调用大模型，但业务含义不同。

## 6. 为什么继续复用 main.py

`api.py` 不应该重新写总结逻辑。

更合理的结构是：

```text
main.py：核心 AI 能力
api.py：把核心能力包装成 HTTP 接口
```

这样以后 Streamlit 页面和 FastAPI 接口都可以复用同一套核心函数。

## 7. 今天怎么测试

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
POST /summarize
```

输入：

```json
{
  "text": "人工智能应用开发通常包括需求分析、模型调用、数据处理、接口封装和前端展示。初学者应该先理解大模型 API 的调用流程，再学习 RAG、工具调用和工程部署。"
}
```

点击 `Execute`。

## 8. 今天你要能讲清楚

1. `/summarize` 为什么用 POST？
2. `/summarize` 和 `/chat` 的输入有什么区别？
3. `SummarizeRequest` 的作用是什么？
4. `SummarizeResponse` 的作用是什么？
5. `api.py` 为什么要复用 `main.py`？
6. 空文本为什么返回 400？


# Day 17：文档问答接口 POST /ask-doc

今天的目标是把完整 RAG 问答包装成 FastAPI 接口。

Day 16 已经完成：

```text
POST /documents
上传 txt -> 切分 chunks -> 写入 Chroma
```

今天完成：

```text
POST /ask-doc
输入问题 -> Chroma 检索 -> LLM 回答 -> 返回引用来源
```

## 1. 今天新增了什么

在 `api.py` 里新增：

```text
POST /ask-doc
```

请求体：

```json
{
  "collection_name": "test_doc",
  "question": "这篇文档主要讲什么？",
  "top_k": 3,
  "min_score": 0.2
}
```

响应体：

```json
{
  "answer": "...",
  "sources": [
    {
      "index": 1,
      "score": 0.78,
      "text": "..."
    }
  ]
}
```

## 2. AskDocRequest 是什么

```python
class AskDocRequest(BaseModel):
    collection_name: str
    question: str
    top_k: int = 3
    min_score: float = 0.2
```

它规定 `/ask-doc` 需要：

```text
collection_name：要查询哪个 Chroma collection
question：用户问题
top_k：最多检索几个 chunks
min_score：最低引用相似度
```

## 3. AskDocResponse 是什么

```python
class AskDocResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
```

它规定返回：

```text
answer：LLM 生成的最终回答
sources：回答使用到的引用片段
```

## 4. SourceChunk 是什么

```python
class SourceChunk(BaseModel):
    index: int
    score: float
    text: str
```

它表示一个引用来源。

每个 source 里有：

```text
index：chunk 编号
score：相似度分数
text：chunk 原文
```

## 5. /ask-doc 内部流程

代码逻辑是：

```text
1. 检查 collection_name 是否为空
2. 检查 question 是否为空
3. 检查 top_k 是否大于 0
4. 检查 min_score 是否在 0 到 1 之间
5. 调用 answer_with_chroma_rag
6. 整理 sources
7. 返回 answer 和 sources
```

## 6. /documents 和 /ask-doc 的关系

`/documents` 是入库：

```text
上传文档 -> 写入 Chroma
```

`/ask-doc` 是查询：

```text
根据 collection_name -> 查询 Chroma -> 调 LLM 回答
```

所以通常顺序是：

```text
先 POST /documents
再 POST /ask-doc
```

## 7. 今天怎么测试

第一步，先上传文档：

```text
POST /documents
```

记住返回的：

```text
collection_name
```

第二步，提问：

```text
POST /ask-doc
```

请求示例：

```json
{
  "collection_name": "test_doc",
  "question": "这篇文档主要讲什么？",
  "top_k": 3,
  "min_score": 0.2
}
```

## 8. 今天你要能讲清楚

1. `/documents` 和 `/ask-doc` 分别做什么？
2. 为什么 `/ask-doc` 需要 collection_name？
3. top_k 是什么？
4. min_score 是什么？
5. 为什么响应里要返回 sources？
6. `/ask-doc` 是怎么复用 `main.py` 的？


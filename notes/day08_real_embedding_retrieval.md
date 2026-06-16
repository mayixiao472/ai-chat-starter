# Day 8：真实 embedding 相似度检索

今天的目标不是学习向量库，而是先把真实 embedding 放进检索流程里。

完整流程是：

```text
上传 txt
-> split_text 切成 chunks
-> create_real_embeddings 给 chunks 批量生成向量
-> create_real_embedding 给问题生成向量
-> dense_cosine_similarity 计算相似度
-> 返回最相关的 top_k 个 chunks
```

## 1. 为什么今天还不用向量库

向量库的作用是“存向量”和“快速查向量”。

但在学习阶段，如果一上来就用 Chroma / FAISS，容易变成只会调用框架，不知道内部发生了什么。

所以今天先手写一个小版本：

```text
问题向量 vs 每个 chunk 向量
```

这虽然不够高效，但最容易看懂。

## 2. 单段 embedding 和批量 embedding 的区别

单段 embedding：

```python
create_real_embedding("我正在学习 AI 应用开发")
```

返回的是：

```text
一条向量
```

批量 embedding：

```python
create_real_embeddings([
    "第一段文本",
    "第二段文本",
    "第三段文本",
])
```

返回的是：

```text
多条向量
```

也就是：

```text
第 1 段文本 -> 第 1 条向量
第 2 段文本 -> 第 2 条向量
第 3 段文本 -> 第 3 条向量
```

## 3. 为什么 response.data[0].embedding 只取第 0 项

如果 input 只传一段文本，API 返回的数据列表里通常只有一项。

所以：

```python
response.data[0].embedding
```

表示取出这唯一一段文本对应的向量。

如果 input 传的是多段文本，就不能只取第 0 项，而应该遍历：

```python
[item.embedding for item in response.data]
```

这就是 `create_real_embeddings` 做的事情。

## 4. 为什么还要算 cosine similarity

embedding API 只负责把文本变成向量。

它不会自动告诉我们哪一段文档最相关。

所以我们还要自己做一步：

```text
问题向量 和 chunk 向量 算相似度
```

相似度越高，说明这段 chunk 越可能回答用户的问题。

## 5. 今天新增的核心函数

在 `main.py` 里：

```python
create_real_embeddings
dense_cosine_similarity
retrieve_chunks_by_real_embedding
```

它们分别负责：

```text
批量生成真实向量
计算真实向量相似度
用真实向量检索相关 chunk
```

## 6. 今天你应该能讲清楚

1. 为什么真实 embedding 检索需要先切分文本？
2. 为什么问题也要生成 embedding？
3. 为什么 chunks 可以批量生成 embedding？
4. 为什么单段输入只取 `response.data[0]`？
5. 为什么多段输入要遍历 `response.data`？
6. 为什么今天还没用 Chroma / FAISS？


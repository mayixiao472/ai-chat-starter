# Day 12：RAG 质量控制

今天的目标是理解：

```text
RAG 不是只要能回答就行，还要尽量避免乱答。
```

Day 11 已经完成了：

```text
Chroma 检索 chunks -> chunks 放进 prompt -> LLM 生成回答
```

今天要补的是质量控制：

```text
检索结果不相关时，不要强行让 LLM 回答。
```

## 1. 为什么需要最低相似度阈值

Chroma 的 `query` 通常会返回 top_k 个结果。

但 top_k 的意思是：

```text
返回最相似的几个
```

不等于：

```text
这几个一定真的相关
```

如果用户问的问题和文档完全无关，Chroma 仍然可能返回几个“相对最像”的 chunk。

所以我们需要设置：

```text
最低相似度阈值
```

低于阈值的 chunk 不应该交给 LLM 当参考资料。

## 2. 今天代码做了什么

在 `main.py` 里，`answer_with_chroma_rag` 增加了：

```python
min_score: float = 0.2
```

然后筛选：

```python
useful_chunks = [
    chunk
    for chunk in retrieved_chunks
    if float(chunk["score"]) >= min_score
]
```

意思是：

```text
只保留相似度达到 min_score 的 chunks
```

## 3. 没有可用 chunks 时怎么办

如果没有任何 chunk 达到阈值，程序会返回：

```text
根据当前资料无法确定。
```

这比硬编一个答案更好。

实习面试里，这一点可以讲成：

```text
我给 RAG 加了相关性阈值，避免无关检索结果进入 prompt，降低幻觉风险。
```

## 4. 阈值越高越好吗

不是。

阈值太低：

```text
容易把无关 chunks 交给 LLM
回答可能乱编
```

阈值太高：

```text
可能把有用 chunks 也过滤掉
系统更容易拒答
```

所以阈值需要根据文档、embedding 模型和测试样例调整。

## 5. 今天页面新增了什么

在“Chroma 向量库”标签页里新增：

```text
RAG 最低引用相似度
```

你可以调节它，观察：

```text
阈值低：更容易回答
阈值高：更容易拒答
```

## 6. 今天你要能讲清楚

1. 为什么 top_k 结果不一定真的相关？
2. 为什么需要 `min_score`？
3. 为什么无关问题应该拒答？
4. 阈值太低有什么风险？
5. 阈值太高有什么风险？
6. 这个改动如何降低 RAG 幻觉？

## 7. 今天的练习

准备两类问题：

```text
和文档相关的问题
和文档无关的问题
```

分别测试：

```text
RAG 最低引用相似度 = 0.1
RAG 最低引用相似度 = 0.3
RAG 最低引用相似度 = 0.5
```

观察回答变化。

你要重点理解：

```text
RAG 的质量不仅取决于 LLM，也取决于检索结果是否真的可靠。
```


# Day 11：完整 RAG 问答

今天的目标是把“Chroma 检索”升级成“完整 RAG 回答”。

之前我们做到的是：

```text
问题 -> embedding -> Chroma -> 相关 chunks
```

这只是检索，不是完整 RAG。

今天补上最后一步：

```text
问题 -> embedding -> Chroma -> 相关 chunks -> prompt -> LLM -> 最终回答
```

## 1. RAG 三个部分

RAG 可以拆成三个词：

```text
Retrieve：检索
Augment：增强
Generate：生成
```

对应到项目里就是：

```text
Retrieve：从 Chroma 找相关 chunks
Augment：把 chunks 拼进 prompt
Generate：调用 LLM 生成回答
```

## 2. 今天新增的核心函数

在 `main.py` 里：

```python
answer_with_chroma_rag
```

它做了四件事：

```text
1. 调用 query_chroma_collection 检索相关 chunks
2. 把 chunks 整理成参考资料 context
3. 构造 messages
4. 调用 ask_llm 得到最终回答
```

## 3. 为什么要把 chunks 拼进 prompt

LLM 本身不知道你的本地文档内容。

Chroma 检索出来的 chunks 只是资料候选。

如果想让 LLM 基于这些资料回答，就必须把 chunks 放进 prompt：

```text
用户问题
参考资料 chunks
回答规则
```

这样 LLM 才知道应该根据哪些资料回答。

## 4. 为什么要显示引用来源

RAG 项目不能只给一个自然语言回答。

更好的做法是同时显示：

```text
最终回答
使用到的 chunks
相似度分数
```

这样用户可以检查回答是否真的来自文档，而不是模型自己编的。

## 5. 现在页面里的两个按钮有什么区别

“检索 Chroma”：

```text
只返回相关 chunks
不调用 LLM
```

“生成 RAG 回答”：

```text
先检索 chunks
再调用 LLM
最后返回自然语言回答和引用来源
```

## 6. 今天你要能讲清楚

1. 为什么 Chroma 检索还不是完整 RAG？
2. RAG 里的 Retrieve、Augment、Generate 分别是什么？
3. 为什么 LLM 需要看到检索出来的 chunks？
4. `answer_with_chroma_rag` 做了哪些步骤？
5. 为什么要显示引用来源？
6. 如果检索结果不准，最终回答会受到什么影响？

## 7. 今天的练习

运行：

```powershell
python -m streamlit run app.py
```

打开“Chroma 向量库”标签页。

先确保已经有 collection。

然后对同一个问题分别点击：

```text
检索 Chroma
生成 RAG 回答
```

观察区别：

```text
检索 Chroma：只给资料片段
生成 RAG 回答：给最终回答，并显示引用来源
```


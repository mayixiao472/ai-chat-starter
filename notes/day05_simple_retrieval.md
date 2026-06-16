# Day 5：简单检索，理解 RAG 的第二步

今天的目标是理解：

```text
用户提问后，程序如何从多个 chunks 里找出相关片段。
```

昨天你学了：

```text
长文档 -> chunks
```

今天继续往前走一步：

```text
用户问题 -> 检索相关 chunks
```

## 1. RAG 为什么需要检索

如果用户只问：

```text
这个项目怎么运行？
```

程序没有必要把整篇文档都发给模型。

更合理的做法是：

```text
先从文档 chunks 里找出和“运行”有关的片段
再把这些片段交给模型回答
```

这就是 RAG 里的 retrieval，也就是“检索”。

## 2. 今天先不用向量库

正式 RAG 通常会用：

```text
embedding + 向量库
```

但今天先不用。

我们先用最容易理解的关键词匹配：

```text
用户问题里出现的词
如果也出现在某个 chunk 里
这个 chunk 的相关分数就增加
```

这不是最聪明的检索方式，但很适合学习检索流程。

## 3. score_chunk 是什么

`main.py` 里新增了：

```python
def score_chunk(query: str, chunk: str) -> int:
```

它的作用是：

```text
给一个 chunk 打分。
分数越高，说明它和用户问题越相关。
```

例如用户问题是：

```text
怎么运行 Streamlit
```

如果某个 chunk 里出现了：

```text
python -m streamlit run app.py
```

这个 chunk 的分数就会更高。

## 4. retrieve_chunks 是什么

`main.py` 里还新增了：

```python
def retrieve_chunks(query: str, chunks: list[str], top_k: int = 3) -> list[dict[str, int | str]]:
```

它的作用是：

```text
从所有 chunks 里，返回分数最高的前 top_k 个。
```

完整流程是：

```text
用户问题
-> 给每个 chunk 打分
-> 按分数排序
-> 取前 top_k 个 chunk
```

## 5. 这和正式 RAG 的区别

今天的简单检索：

```text
关键词匹配
```

正式 RAG 的向量检索：

```text
语义相似度匹配
```

关键词匹配只能发现字面上相同或相近的词。

向量检索可以发现语义相近的内容。

比如：

```text
用户问：怎么启动网页？
文档写：运行 streamlit run app.py。
```

关键词检索可能找不到，因为“启动网页”和“运行 streamlit”字面不一样。

向量检索更可能找得到，因为它比较的是语义。

## 6. 今天你要能讲清楚

请用自己的话回答：

1. RAG 为什么需要检索？
2. `score_chunk` 做了什么？
3. `retrieve_chunks` 做了什么？
4. `top_k` 是什么？
5. 关键词检索有什么缺点？
6. 为什么下一步要学 embedding？

## 7. 今天的练习

运行：

```powershell
python -m streamlit run app.py
```

打开“简单检索”标签页。

上传一个 `.txt` 文件，然后输入关键词，例如：

```text
Streamlit
运行
API
messages
```

观察：

```text
同一个文档，在不同关键词下，会返回不同的 chunks。
```

今天最重要的是理解：

```text
检索不是让模型回答，而是先帮模型找到资料。
```


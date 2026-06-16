# Day 6：embedding 和相似度

今天的目标是理解：

```text
文本为什么可以变成向量，向量为什么可以用来做检索。
```

先记住一句话：

```text
embedding 是把文本变成数字向量。
相似度检索是比较“问题向量”和“chunk 向量”有多像。
```

## 1. 为什么需要 embedding

Day 5 的简单检索是关键词匹配。

它的问题是：只能找字面上相同的词。

比如用户问：

```text
怎么启动网页？
```

文档里写：

```text
运行 python -m streamlit run app.py
```

关键词检索可能找不到，因为“启动网页”和“运行 Streamlit”字面不一样。

embedding 想解决的是：

```text
不只看字面相同，还要看语义相近。
```

## 2. 什么是向量

向量可以先理解成一串数字。

比如：

```text
[0.12, -0.03, 0.88, ...]
```

正式 embedding 模型会把一句话变成这样的数字列表。

语义相近的文本，向量方向通常更接近。

语义差很远的文本，向量方向通常更远。

## 3. 今天为什么用玩具 embedding

真正的 embedding 通常需要调用模型 API 或下载本地模型。

为了先理解原理，今天项目里用了一个玩具版本：

```text
文本 -> token -> 词频向量
```

例如：

```text
Streamlit 可以运行网页
```

会变成类似：

```text
{
  "streamlit": 1,
  "可": 1,
  "以": 1,
  "运": 1,
  "行": 1,
  "网": 1,
  "页": 1
}
```

这不是真正生产级 embedding，但能帮你理解：

```text
文本可以被转换成向量。
向量之间可以计算相似度。
```

## 4. cosine similarity 是什么

项目里新增了：

```python
def cosine_similarity(vector_a, vector_b) -> float:
```

它计算两个向量的余弦相似度。

你不用死记数学公式，先记住结果含义：

```text
越接近 1：越相似
越接近 0：越不相关
```

RAG 里常见的向量检索，本质上就是：

```text
把问题变成向量
把 chunks 变成向量
比较问题向量和每个 chunk 向量的相似度
返回最相似的几个 chunks
```

## 5. 今天新增了哪些函数

`main.py` 里新增：

```python
tokenize_text
create_toy_embedding
cosine_similarity
retrieve_chunks_by_toy_embedding
build_toy_vector_index
search_toy_vector_index
```

它们组成的流程是：

```text
问题 -> 玩具向量
chunk -> 玩具向量
计算相似度
返回相似度最高的 chunks
```

后面两个函数是为了理解“向量索引”：

```text
build_toy_vector_index：提前给所有 chunks 计算向量
search_toy_vector_index：每次提问时，只计算 query 向量，再和已有 chunk 向量比较
```

这样同一份文档不变时，就不用每次都重复计算所有 chunk 的向量。

真实向量库也是类似思路：

```text
文档向量提前存好。
用户每次提问时，只计算问题向量。
再从已保存的文档向量里找最相似的 chunks。
```

## 6. 玩具 embedding 和正式 embedding 的区别

玩具 embedding：

```text
基于词频
容易理解
不需要 API
不能真正理解语义
```

正式 embedding：

```text
由 embedding 模型生成
数字维度更多
能表达更复杂的语义
通常配合向量库使用
```

所以今天不是最终方案，而是为了理解正式 RAG 的骨架。

## 7. 今天你要能讲清楚

请用自己的话回答：

1. embedding 是什么？
2. 为什么关键词检索不够好？
3. 向量相似度在 RAG 里解决什么问题？
4. cosine similarity 的结果越大代表什么？
5. 玩具 embedding 和正式 embedding 有什么区别？
6. 为什么下一步要学习向量库？

## 8. 今天的练习

运行：

```powershell
python -m streamlit run app.py
```

打开“向量相似度”标签页。

上传 `.txt` 文件，然后输入一个问题，观察系统返回哪些 chunks。

今天最重要的是理解：

```text
embedding 不是模型回答问题。
embedding 是为了把文本变成可比较的数字向量。
```

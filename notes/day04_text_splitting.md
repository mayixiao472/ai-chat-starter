# Day 4：文本切分，为 RAG 做准备

今天的目标是理解：

```text
为什么长文档不能直接全部发给模型，而要先切成小块。
```

这一天开始，你正式从“文件总结”走向 RAG。

## 1. 为什么要切分文本

如果文档很短，可以直接这样做：

```text
把整段文本放进 prompt -> 让模型总结
```

但真实项目里的文档可能很长，比如：

- 一篇论文
- 一本说明书
- 一堆项目文档
- 一份很长的实验报告

如果全部发给模型，会有几个问题：

- 文本太长，请求会变慢
- token 消耗会增加
- 可能超过模型上下文长度
- 模型容易抓不住重点
- 用户只问一个小问题时，没必要把整篇文档都发过去

所以 RAG 的第一步通常是：

```text
长文档 -> 切成多个小片段
```

## 2. 什么是 chunk

chunk 可以理解成“文本块”。

比如原文是：

```text
第一段内容。第二段内容。第三段内容。第四段内容。
```

切分后可能变成：

```text
chunk 1：第一段内容。第二段内容。
chunk 2：第三段内容。第四段内容。
```

后面做 RAG 时，不会把整篇文章都发给模型。

而是：

```text
用户提问 -> 找到最相关的几个 chunk -> 把这些 chunk 发给模型
```

## 3. 最简单的切分方式

最容易理解的方式是按字符数量切。

比如每 500 个字符切一块：

```python
def split_text(text: str, chunk_size: int = 500) -> list[str]:
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)

    return chunks
```

这段代码的意思是：

```text
从第 0 个字符开始，每次取 500 个字符，放进 chunks 列表。
```

## 4. 为什么需要 overlap

只按固定长度切，会有一个问题：

```text
一句重要的话可能被切断在两个 chunk 中间。
```

比如：

```text
chunk 1：RAG 的核心是先检索相关文档片段，然后
chunk 2：再把片段交给大模型回答问题。
```

如果没有重叠，单独看 chunk 1 或 chunk 2 都不完整。

所以常见做法是加入 overlap，也就是相邻 chunk 之间保留一小段重复内容。

例如：

```text
chunk 1：RAG 的核心是先检索相关文档片段，然后再把片段
chunk 2：然后再把片段交给大模型回答问题。
```

这样模型或检索系统更不容易丢上下文。

## 5. 带 overlap 的切分逻辑

可以这样理解：

```text
chunk_size：每块文本最大多长
overlap：下一块和上一块重复多少字符
step：每次向前移动多少字符
```

如果：

```text
chunk_size = 500
overlap = 100
```

那么：

```text
step = 500 - 100 = 400
```

也就是说：

```text
第 1 块：0 到 500
第 2 块：400 到 900
第 3 块：800 到 1300
```

中间重叠的 100 个字符，就是为了保留上下文。

## 6. 这和 RAG 的关系

RAG 的完整流程以后会是：

```text
读取文档
-> 文本切分成 chunks
-> 给每个 chunk 生成 embedding
-> 用户提问也生成 embedding
-> 找到最相似的 chunks
-> 把相关 chunks 放进 prompt
-> 模型基于资料回答
```

今天只学第一步：

```text
文本切分成 chunks
```

不要急着上向量库。

## 7. 今天你要能讲清楚

请用自己的话回答：

1. 为什么不能一直把整篇文档都发给模型？
2. chunk 是什么？
3. `chunk_size` 是什么？
4. overlap 是什么？
5. 为什么 overlap 能减少信息断裂？
6. 文本切分在 RAG 流程里处于哪一步？

## 8. 今天的练习

先不要做复杂网页。

今天只需要理解这个函数：

```python
def split_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = start + chunk_size - overlap

    return chunks
```

你要能说清楚：

```text
start 是当前 chunk 的起点。
end 是当前 chunk 的终点。
chunk_size 控制每块多长。
overlap 控制相邻块重复多少。
start 每次向前移动 chunk_size - overlap。
```

这个函数已经加进项目里了。

你可以运行：

```powershell
python -m streamlit run app.py
```

然后打开“文本切分”标签页，上传 `.txt` 文件，调整 `chunk_size` 和 `overlap`，观察同一篇文本会被切成多少块。

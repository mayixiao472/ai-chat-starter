# Day 9：真实 embedding 缓存和索引思想

今天的目标是理解：

```text
同一份文档不变时，不应该每次提问都重新计算所有 chunk 向量。
```

你之前提出的效率问题是对的：

```text
如果 txt 文件不变，只是用户换了一个问题，chunk 的 embedding 应该复用。
```

## 1. Day 8 的做法有什么问题

Day 8 的流程是：

```text
用户提问
-> 切分文档
-> 给所有 chunks 生成真实 embedding
-> 给问题生成真实 embedding
-> 计算相似度
-> 返回 top_k chunks
```

这个流程能跑通，但有一个明显问题：

```text
用户每换一个问题，所有 chunk 向量都会重新生成一遍。
```

如果文档有很多 chunks，这会浪费时间，也会浪费 embedding API 额度。

## 2. 更合理的做法

文档不变时，应该先做一次：

```text
读取文档
-> 切分 chunks
-> 给 chunks 批量生成 embedding
-> 保存成 vector_index
```

之后每次用户提问，只需要：

```text
给问题生成 embedding
-> 和已有的 chunk 向量计算相似度
-> 返回最相关 chunks
```

这就是“索引”的核心思想。

## 3. 今天新增的核心函数

在 `main.py` 里：

```python
build_real_vector_index
search_real_vector_index
```

它们的分工是：

```text
build_real_vector_index：提前给 chunks 生成真实向量，保存起来
search_real_vector_index：用户提问时，只生成问题向量，再搜索已有索引
```

你可以把它们理解成：

```text
建库
查库
```

虽然现在还没有真的使用 Chroma / FAISS，但思想已经很接近了。

## 4. vector_index 里面保存什么

现在的 `vector_index` 是一个列表，每个元素大概长这样：

```python
{
    "index": 1,
    "text": "某个 chunk 的原文",
    "vector": [0.01, -0.03, 0.12, ...],
}
```

这三项分别表示：

```text
index：这是第几个 chunk
text：chunk 原文
vector：chunk 的真实 embedding
```

正式向量库以后也会保存类似内容，只是会更高效，还会保存更多 metadata。

## 5. st.cache_data 在这里做什么

在 `app.py` 里：

```python
@st.cache_data
def build_cached_real_vector_index(...):
```

它的作用是：

```text
同一份文本
同样的 chunk_size
同样的 overlap
同样的 max_chunks
```

只要这些输入不变，Streamlit 就复用上一次建好的真实向量索引。

这样你换问题时，不需要重新给所有 chunks 调 embedding API。

## 6. 为什么仍然不是正式向量库

现在的缓存索引适合教学和小 Demo：

```text
简单
直观
方便理解
适合少量 chunks
```

但它还不是正式向量库，因为：

```text
不能很好管理大量文档
不能持久化成一个专业数据库
不方便做 metadata 过滤
检索速度和扩展性有限
```

正式向量库，比如 Chroma / FAISS，会帮我们更好地保存和搜索大量向量。

## 7. 今天你要能讲清楚

1. 为什么 Day 8 的真实 embedding 检索会浪费？
2. 为什么 chunk 向量可以缓存？
3. 用户换问题时，为什么只需要重新计算 query 向量？
4. `build_real_vector_index` 是做什么的？
5. `search_real_vector_index` 是做什么的？
6. `st.cache_data` 在这里解决了什么问题？
7. 现在的缓存索引和 Chroma / FAISS 有什么区别？

## 8. 今天的练习

运行：

```powershell
python -m streamlit run app.py
```

打开“真实向量检索”标签页。

上传同一个 txt 文件，连续换几个问题，观察页面显示：

```text
已缓存 N 个真实 chunk 向量
```

你要理解：

```text
文件不变时，chunk 向量应该复用。
问题变化时，只需要重新计算问题向量。
```


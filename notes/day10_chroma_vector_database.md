# Day 10：Chroma 向量数据库

今天直接进入 Chroma。

你的判断是对的：真实 RAG 项目通常不会用 JSON 文件当正式向量库。我们现在要学习的是更接近项目实践的写法：

```text
文档 -> chunks -> embedding -> Chroma
问题 -> embedding -> Chroma 检索 -> 相关 chunks
```

## 1. Chroma 是什么

Chroma 是一个向量数据库。

在这个项目里，你可以先把它理解成：

```text
专门保存 chunk 文本和 chunk 向量的数据库
```

它保存的不只是向量，还可以保存：

```text
document：chunk 原文
embedding：chunk 的向量
metadata：文件名、chunk 编号、来源等信息（元数据，描述数据的数据）
id：每条数据的唯一编号
```

## 2. 为什么要用 Chroma

如果不用向量库，每次提问可能都要重新：

```text
切分文档
生成所有 chunk 的 embedding
遍历所有向量计算相似度
```

用了 Chroma 后，可以变成：

```text
第一次：把文档 chunks 和 embeddings 存进 Chroma
之后：只给问题生成 embedding，然后让 Chroma 检索相似 chunks
```

这更接近真实 RAG 项目的结构。

## 3. 今天新增的核心函数

在 `main.py` 里：

```python
create_chroma_client
save_chunks_to_chroma
query_chroma_collection
list_chroma_collections
```

它们分别负责：

```text
创建 Chroma 客户端
把 chunks 存进 Chroma
从 Chroma 里检索相关 chunks
列出已有的 collections
```

## 4. collection 是什么

Chroma 里用 collection 管理一组向量。

你可以先把 collection 理解成：

```text
一个文档集合
```

例如：

```text
my_first_doc
sft_net_paper
internship_notes
```

每个 collection 里面可以保存很多 chunks。

## 5. save_chunks_to_chroma 做了什么

流程是：

```text
接收 chunks
-> 调用 create_real_embeddings 生成真实 embedding
-> 为每个 chunk 生成 id
-> 准备 metadata
-> collection.upsert 写入 Chroma
```

其中：

```python
collection.upsert(...)
```

意思是：

```text
如果 id 不存在，就新增
如果 id 已存在，就更新
```

## 6. query_chroma_collection 做了什么

流程是：

```text
接收用户问题
-> 调用 create_real_embedding 生成问题向量
-> collection.query 从 Chroma 检索相似 chunks
-> 返回文本、metadata、距离分数
```

注意：

```text
embedding API 负责把文本变向量
Chroma 负责保存向量和检索相似向量
```

这两个职责不要混在一起。

## 7. Chroma 和 FAISS 的简单区别

第一个月建议先学 Chroma。

原因是：

```text
Chroma 更像完整向量数据库
它能保存 documents、embeddings、metadata
更适合 RAG 入门项目
```

FAISS 更偏底层相似度检索库，检索能力强，但很多文档管理、metadata 管理要自己补。

## 8. 今天你要能讲清楚

1. Chroma 在 RAG 里负责什么？
2. embedding API 和 Chroma 的职责有什么区别？
3. collection 是什么？
4. 为什么第一次要把 chunks 存进 Chroma？
5. 用户提问时，为什么只需要给问题生成 embedding？
6. `collection.upsert` 是做什么的？
7. `collection.query` 是做什么的？

## 9. 今天的练习

先安装新依赖：

```powershell
python -m pip install -r requirements.txt
```

运行项目：

```powershell
python -m streamlit run app.py
```

打开“Chroma 向量库”标签页。

第一步：

```text
上传 txt
输入 collection 名称
点击“生成 embedding 并保存到 Chroma”
```

第二步：

```text
选择 collection
输入问题
点击“检索 Chroma”
```

你今天只需要抓住这句话：

```text
Chroma 保存 chunk 向量；用户提问时，Chroma 帮我们找相似 chunk。
```


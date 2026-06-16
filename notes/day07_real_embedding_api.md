# Day 7：真实 embedding API

今天的目标是理解：

```text
如何调用真实 embedding API，把一段文本变成真实向量。
```

Day 6 用的是玩具 embedding：

```text
文本 -> token -> 词频向量
```

Day 7 开始进入真实 embedding：

```text
文本 -> embedding 模型 API -> 一串浮点数向量
```

## 1. 先纠正一个容易混淆的点

聊天模型和 embedding 模型不是同一种任务。

聊天模型负责：

```text
输入 messages -> 输出自然语言回答
```

embedding 模型负责：

```text
输入文本 -> 输出数字向量
```

所以：

```text
DeepSeek 聊天 API 能回答问题，但不等于它一定提供 embedding API。
```

如果一个平台没有 embedding endpoint，就不能把聊天模型硬当 embedding 模型用。

## 2. 真实 embedding API 返回什么

真实 embedding API 通常返回一个数字列表：

```text
[0.0123, -0.0456, 0.0789, ...]
```

这个列表就是向量。

你不用记住每个数字是什么意思，只需要知道：

```text
语义相近的文本，向量通常更接近。
语义差很远的文本，向量通常更远。
```

## 3. 为什么要单独配置 embedding

你的聊天模型现在可以用 DeepSeek。

但 embedding 模型可以来自另一个平台，比如：

```text
OpenAI embedding
Jina embedding
阿里 DashScope embedding
火山方舟 embedding
本地 bge / Qwen embedding
```

所以项目里把聊天配置和 embedding 配置分开：

```text
DEEPSEEK_API_KEY：聊天用
OPENAI_BASE_URL：聊天接口地址
OPENAI_MODEL：聊天模型

EMBEDDING_API_KEY：embedding 用
EMBEDDING_BASE_URL：embedding 接口地址
EMBEDDING_MODEL：embedding 模型
EMBEDDING_DIMENSIONS：embedding 向量维度，可选
EMBEDDING_ENCODING_FORMAT：embedding 返回格式，可选
```

这样做更清楚，也更接近真实项目。

## 4. 今天新增了什么

`main.py` 里新增：

```python
create_embedding_client
create_real_embedding
```

它们的流程是：

```text
读取 .env 里的 embedding 配置
-> 创建 embedding API 客户端
-> 调用 embeddings.create
-> 取出 response.data[0].embedding
-> 得到真实向量
```

## 5. app.py 里新增了什么

网页里新增了：

```text
真实 embedding API
```

你可以输入一句话，然后点击按钮。

如果配置正确，页面会显示：

```text
向量维度
前 10 个向量值
```

这一步不是 RAG，只是先验证：

```text
我能把一句话变成真实 embedding 向量。
```

## 6. 今天你要能讲清楚

请用自己的话回答：

1. 聊天模型和 embedding 模型有什么区别？
2. 为什么 DeepSeek 聊天 API 不等于 embedding API？
3. 真实 embedding API 返回的是什么？
4. 为什么 embedding 配置要和聊天配置分开？
5. `response.data[0].embedding` 取出的是什么？
6. 为什么下一步才能用真实 embedding 做相似度检索？

## 7. 今天的练习

先阅读代码，不急着充值或注册新平台。

重点看：

```text
main.py 里的 create_real_embedding
app.py 里的“真实 embedding API”标签页
```

如果你已经有可用的 embedding API，就在 `.env` 里配置：

```text
EMBEDDING_API_KEY=你的embedding平台key
EMBEDDING_BASE_URL=你的embedding平台base_url
EMBEDDING_MODEL=你的embedding模型名
```

如果使用阿里云百炼 DashScope，可以配置：

```text
EMBEDDING_API_KEY=你的百炼API key
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_DIMENSIONS=1024
EMBEDDING_ENCODING_FORMAT=float
```

也可以把 key 写成阿里官方常见变量名：

```text
DASHSCOPE_API_KEY=你的百炼API key
```

然后运行：

```powershell
python -m streamlit run app.py
```

打开“真实 embedding API”标签页，输入：

```text
我正在学习 AI 应用开发。
```

观察返回的向量维度和前 10 个数字。


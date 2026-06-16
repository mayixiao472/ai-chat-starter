# Day 16：文档上传接口 POST /documents

今天的目标是把“上传 txt 并写入 Chroma”包装成 FastAPI 接口。

之前在 Streamlit 里做的是：

```text
上传 txt
-> 读取文本
-> split_text 切分 chunks
-> embedding
-> 写入 Chroma
```

今天变成：

```text
前端 / 其他程序
-> POST /documents
-> FastAPI 读取上传文件
-> 切分 chunks
-> 写入 Chroma
-> 返回 JSON
```

## 1. 今天新增了什么

在 `api.py` 里新增：

```text
POST /documents
```

这个接口不是普通 JSON 请求，而是文件上传请求。

## 2. 为什么文件上传不是普通 JSON

`/chat` 和 `/summarize` 传的是普通文本，所以可以用 JSON：

```json
{
  "question": "..."
}
```

但 `/documents` 要上传文件，所以使用：

```text
multipart/form-data
```

在 FastAPI 里对应：

```python
file: UploadFile = File(...)
```

## 3. UploadFile 是什么

`UploadFile` 表示用户上传的文件。

它里面有：

```text
file.filename：文件名
await file.read()：读取文件内容
```

今天我们只支持 `.txt` 文件。

## 4. Form 是什么

除了文件之外，我们还希望用户传一些参数：

```text
collection_name
chunk_size
overlap
max_chunks
```

因为这是文件上传接口，所以这些字段用：

```python
Form(...)
```

而不是 `BaseModel`。

## 5. /documents 内部流程

代码逻辑是：

```text
1. 检查文件是不是 .txt
2. 读取文件 bytes
3. decode 成字符串
4. 检查文本是否为空
5. split_text 切成 chunks
6. 只取前 max_chunks 个 chunks
7. save_chunks_to_chroma 写入 Chroma
8. 返回文件名、collection 名称、chunk 数量
```

## 6. chunk_count 和 indexed_count 的区别

响应里有两个数量：

```text
chunk_count：整篇文档一共切成多少个 chunks
indexed_count：这次实际写入 Chroma 多少个 chunks
```

为什么可能不一样？

因为学习阶段我们用：

```text
max_chunks
```

限制最多入库多少个 chunk，避免一次消耗太多 embedding API 额度。

## 7. 今天怎么测试

启动：

```powershell
python -m uvicorn api:app --reload
```

打开：

```text
http://127.0.0.1:8000/docs
```

找到：

```text
POST /documents
```

点击 `Try it out`，上传一个 `.txt` 文件。

可以先用这些参数：

```text
collection_name: test_doc
chunk_size: 500
overlap: 100
max_chunks: 5
```

## 8. 今天你要能讲清楚

1. `/documents` 为什么用 POST？
2. 为什么文件上传不用普通 JSON？
3. `UploadFile` 是什么？
4. `File(...)` 和 `Form(...)` 分别表示什么？
5. `chunk_count` 和 `indexed_count` 有什么区别？
6. 为什么上传文档后要写入 Chroma？


# Day 19：FastAPI 连接 MySQL

今天的目标是把 FastAPI 和 MySQL 连起来。

Day 18 学的是 MySQL 基础：

```text
表
字段
主键
INSERT
SELECT
```

今天把它接入项目：

```text
POST /documents
-> 写入 Chroma
-> 写入 MySQL 文档记录
```

并新增：

```text
GET /documents
```

用于查询已经上传过的文档记录。

## 1. 今天新增了什么

新增文件：

```text
database.py
```

新增依赖：

```text
pymysql
```

新增接口：

```text
GET /documents
```

## 2. database.py 负责什么

`database.py` 是数据库操作层。

它负责：

```text
读取 MySQL 配置
创建 MySQL 连接
创建 documents 表
插入文档记录
查询文档记录
```

这样 `api.py` 不需要直接写很多 SQL。

## 3. MySQL 配置在哪里

在 `.env` 里配置：

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=ai_chat_starter
```

`.env.example` 里已经有模板。

## 4. POST /documents 现在多做了什么

之前：

```text
上传 txt
-> 切分 chunks
-> 写入 Chroma
-> 返回结果
```

现在：

```text
上传 txt
-> 切分 chunks
-> 写入 Chroma
-> 写入 MySQL documents 表
-> 返回结果
```

返回里新增：

```text
id
```

表示 MySQL 里新插入的文档记录 id。

## 5. GET /documents 做什么

`GET /documents` 会从 MySQL 查询文档记录。

返回示例：

```json
[
  {
    "id": 1,
    "filename": "example.txt",
    "collection_name": "example",
    "chunk_count": 12,
    "indexed_count": 5,
    "created_at": "2026-06-09 12:00:00"
  }
]
```

## 6. Chroma 和 MySQL 的分工

Chroma 保存：

```text
chunk 原文
chunk embedding
metadata
```

MySQL 保存：

```text
文档记录
collection 名称
上传时间
chunk 数量
```

你可以这样讲：

```text
Chroma 负责向量检索，MySQL 负责业务数据管理。
```

## 7. 今天怎么测试

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

确认 `.env` 里 MySQL 配置正确。

启动：

```powershell
python -m uvicorn api:app --reload
```

测试顺序：

```text
1. POST /documents 上传 txt
2. GET /documents 查看 MySQL 里的文档记录
3. POST /ask-doc 用 collection_name 提问
```

## 8. 今天你要能讲清楚

1. 为什么 AI 应用还需要 MySQL？
2. 为什么向量不放 MySQL，而是放 Chroma？
3. `database.py` 负责什么？
4. `POST /documents` 现在多写入了什么？
5. `GET /documents` 从哪里查询数据？
6. MySQL 里的 `id` 和 Chroma 的 `collection_name` 分别有什么用？


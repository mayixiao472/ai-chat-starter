# Day 18：MySQL 基础

今天的目标是理解：

```text
AI 应用里为什么需要 MySQL，以及 MySQL 保存什么。
```

在我们的项目里：

```text
Chroma：保存 chunk 向量，用来做相似度检索
MySQL：保存业务记录，用来管理文档信息
```

## 1. 为什么不用 MySQL 保存向量

向量检索需要计算相似度，适合交给 Chroma 这种向量数据库。

MySQL 更适合保存结构化业务数据，比如：

```text
文档 id
文件名
Chroma collection 名称
chunk 数量
上传时间
```

所以不要把两者混在一起：

```text
Chroma 管向量
MySQL 管记录
```

## 2. 今天新增了什么

新增文件：

```text
mysql_schema.sql
```

它里面包含：

```text
创建数据库
创建 documents 表
INSERT 插入
SELECT 查询
UPDATE 修改
DELETE 删除
```

## 3. documents 表保存什么

表结构是：

```sql
CREATE TABLE IF NOT EXISTS documents (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  filename VARCHAR(255) NOT NULL,
  collection_name VARCHAR(255) NOT NULL,
  chunk_count INT NOT NULL,
  indexed_count INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

字段含义：

```text
id：主键，每条记录的唯一编号
filename：上传的文件名
collection_name：对应的 Chroma collection 名称
chunk_count：文档一共切成多少个 chunks
indexed_count：实际写入 Chroma 的 chunks 数量
created_at：上传时间
```

## 4. 主键是什么

主键就是一条记录的唯一标识。

例如：

```text
id = 1 表示第 1 条文档记录
id = 2 表示第 2 条文档记录
```

这里使用：

```sql
id BIGINT PRIMARY KEY AUTO_INCREMENT
```

意思是：

```text
id 是主键
id 自动递增
插入数据时不用手动填写 id
```

## 5. INSERT 是什么

`INSERT` 用来新增数据。

例如：

```sql
INSERT INTO documents (
  filename,
  collection_name,
  chunk_count,
  indexed_count
) VALUES (
  'example.txt',
  'example',
  12,
  5
);
```

意思是：

```text
新增一条文档记录
```

## 6. SELECT 是什么

`SELECT` 用来查询数据。

例如：

```sql
SELECT * FROM documents;
```

意思是：

```text
查询 documents 表里的所有记录
```

项目里更常用：

```sql
SELECT
  id,
  filename,
  collection_name,
  chunk_count,
  indexed_count,
  created_at
FROM documents
ORDER BY created_at DESC;
```

意思是：

```text
按上传时间倒序查询文档列表
```

## 7. UPDATE 和 DELETE 是什么

`UPDATE` 用来修改：

```sql
UPDATE documents
SET filename = 'updated_example.txt'
WHERE id = 1;
```

`DELETE` 用来删除：

```sql
DELETE FROM documents
WHERE id = 1;
```

注意：

```text
UPDATE 和 DELETE 一般都要带 WHERE
```

否则可能会修改或删除整张表。

## 8. 今天你要能讲清楚

1. Chroma 和 MySQL 的分工是什么？
2. 为什么 MySQL 不负责向量相似度检索？
3. documents 表保存哪些字段？
4. 主键 id 是什么？
5. INSERT / SELECT / UPDATE / DELETE 分别做什么？
6. 为什么 UPDATE / DELETE 要小心 WHERE？

## 9. 明天要做什么

明天会把 FastAPI 连接 MySQL：

```text
POST /documents 上传文档
-> 写入 Chroma
-> 同时把文档记录写入 MySQL
```

然后新增：

```text
GET /documents
```

用于从 MySQL 查询已经上传过的文档记录。


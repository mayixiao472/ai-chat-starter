-- Day 18: MySQL 基础表结构和 CRUD 示例
-- 这个文件先用于学习和手动执行，不会被 Python 自动运行。

CREATE DATABASE IF NOT EXISTS ai_chat_starter
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE ai_chat_starter;

CREATE TABLE IF NOT EXISTS documents (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  filename VARCHAR(255) NOT NULL,
  collection_name VARCHAR(255) NOT NULL,
  chunk_count INT NOT NULL,
  indexed_count INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 插入一条文档记录。
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

-- 查询所有文档记录，最新上传的排在前面。
SELECT
  id,
  filename,
  collection_name,
  chunk_count,
  indexed_count,
  created_at
FROM documents
ORDER BY created_at DESC;

-- 按 id 查询一条文档记录。
SELECT
  id,
  filename,
  collection_name,
  chunk_count,
  indexed_count,
  created_at
FROM documents
WHERE id = 1;

-- 修改一条文档记录的文件名。
UPDATE documents
SET filename = 'updated_example.txt'
WHERE id = 1;

-- 删除一条文档记录。
DELETE FROM documents
WHERE id = 1;

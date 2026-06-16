import os
from datetime import datetime

import pymysql
from dotenv import load_dotenv


def load_database_config() -> None:
    """加载 .env 里的 MySQL 配置。"""
    load_dotenv(override=True)


def create_mysql_connection():
    """创建 MySQL 连接。"""
    load_database_config()

    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "ai_chat_starter"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def create_documents_table() -> None:
    """如果 documents 表不存在，就创建它。"""
    sql = """
    CREATE TABLE IF NOT EXISTS documents (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      filename VARCHAR(255) NOT NULL,
      collection_name VARCHAR(255) NOT NULL,
      chunk_count INT NOT NULL,
      indexed_count INT NOT NULL,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """

    connection = create_mysql_connection()
    try:
        with connection.cursor() as cursor:  #.cursor创建游标，相当于在图书馆拿个小推车，用小推车来拿/放图书管理的书
            cursor.execute(sql) #执行sql语句
    finally:
        connection.close()


def insert_document_record(
    filename: str,
    collection_name: str,
    chunk_count: int,
    indexed_count: int,
) -> int:
    """插入一条文档记录，并返回新记录的 id。"""
    create_documents_table()

    sql = """
    INSERT INTO documents (
      filename,
      collection_name,
      chunk_count,
      indexed_count
    ) VALUES (
      %s,
      %s,
      %s,
      %s
    );
    """

    connection = create_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    filename,
                    collection_name,
                    chunk_count,
                    indexed_count,
                ),
            )
            return int(cursor.lastrowid)
    finally:
        connection.close()


def list_document_records() -> list[dict[str, int | str | datetime]]:
    """查询所有文档记录。"""
    create_documents_table()

    sql = """
    SELECT
      id,
      filename,
      collection_name,
      chunk_count,
      indexed_count,
      created_at
    FROM documents
    ORDER BY created_at DESC;
    """

    connection = create_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return list(cursor.fetchall())
    finally:
        connection.close()

import argparse
import math
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)


CHROMA_DB_DIR = Path(__file__).with_name("chroma_db")


def load_config() -> None:
    """加载 .env 文件。

    .env 里放 API key、模型名、接口地址等配置。
    这些内容不要直接写进代码，因为 API key 属于私人密钥。
    """
    env_path = Path(__file__).with_name(".env")
    load_dotenv(dotenv_path=env_path, override=True)


def create_client() -> OpenAI:
    """创建大模型 API 客户端。

    客户端可以理解成“帮我们向大模型服务发送请求的工具”。
    这里虽然使用的是 openai 这个 Python 包，但接口地址可以配置成 DeepSeek。
    """
    load_config()

    deepseek_api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    openai_api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    api_key = deepseek_api_key or openai_api_key

    base_url = (os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com").strip()

    if not api_key:
        raise RuntimeError(
            "没有找到 API key。\n"
            "如果你使用 DeepSeek，请在 .env 里填写 DEEPSEEK_API_KEY。"
        )

    if api_key in {"your_deepseek_api_key_here", "your_api_key_here"}:
        raise RuntimeError(
            "你还没有填写真正的 API key。\n"
            "请把 .env 里的占位文字换成你的真实 DeepSeek API key。"
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def create_embedding_client() -> OpenAI:
    """创建 embedding API 客户端。

    embedding 模型和聊天模型可以来自不同平台，所以这里单独读取
    EMBEDDING_API_KEY / DASHSCOPE_API_KEY 和 EMBEDDING_BASE_URL。
    """
    load_config()

    api_key = (
        os.getenv("EMBEDDING_API_KEY")
        or os.getenv("DASHSCOPE_API_KEY")
        or ""
    ).strip()
    base_url = (os.getenv("EMBEDDING_BASE_URL") or "").strip()

    if not api_key:
        raise RuntimeError(
            "没有找到 EMBEDDING_API_KEY 或 DASHSCOPE_API_KEY。\n"
            "聊天 API key 和 embedding API key 可能不是同一个，请在 .env 里单独配置。"
        )

    if api_key == "your_embedding_api_key_here":
        raise RuntimeError(
            "你还没有填写真正的 embedding API key。\n"
            "请把 .env 里的 EMBEDDING_API_KEY 占位文字换成真实 key。"
        )

    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)

    return OpenAI(api_key=api_key)


def create_real_embedding(text: str) -> list[float]:
    """调用真实 embedding API，把文本转换成向量。"""
    text = text.strip()
    if not text:
        raise ValueError("文本不能为空。")

    client = create_embedding_client()
    model = (os.getenv("EMBEDDING_MODEL") or "").strip()
    if not model:
        raise RuntimeError(
            "没有找到 EMBEDDING_MODEL。\n"
            "请在 .env 里写清楚你要使用的 embedding 模型，例如阿里云的 text-embedding-v4。"
        )

    dimensions = (os.getenv("EMBEDDING_DIMENSIONS") or "").strip()
    encoding_format = (os.getenv("EMBEDDING_ENCODING_FORMAT") or "").strip()

    request_kwargs: dict[str, object] = {
        "model": model,
        "input": text,
    }

    if dimensions:
        request_kwargs["dimensions"] = int(dimensions)

    if encoding_format:
        request_kwargs["encoding_format"] = encoding_format

    response = client.embeddings.create(**request_kwargs)

    return response.data[0].embedding


def create_real_embeddings(texts: list[str]) -> list[list[float]]:
    """批量调用真实 embedding API，把多段文本转换成多条向量。"""
    cleaned_texts = [text.strip() for text in texts if text.strip()]
    """第126行代码等价于下面的代码
    cleaned_texts = []
    for text in texts:
        if text.strip():
            cleaned_texts.append(text.strip())
    """
    if not cleaned_texts:
        raise ValueError("文本列表不能为空。")

    client = create_embedding_client()
    model = (os.getenv("EMBEDDING_MODEL") or "").strip()
    if not model:
        raise RuntimeError(
            "没有找到 EMBEDDING_MODEL。\n"
            "请在 .env 里写清楚你要使用的 embedding 模型。"
        )

    dimensions = (os.getenv("EMBEDDING_DIMENSIONS") or "").strip()
    encoding_format = (os.getenv("EMBEDDING_ENCODING_FORMAT") or "").strip()

    request_kwargs: dict[str, object] = {
        "model": model,
        "input": cleaned_texts,
    }

    if dimensions:
        request_kwargs["dimensions"] = int(dimensions)

    if encoding_format:
        request_kwargs["encoding_format"] = encoding_format

    response = client.embeddings.create(**request_kwargs)
    return [item.embedding for item in response.data]


def create_initial_messages() -> list[dict[str, str]]:
    """创建聊天开始时的 messages 列表。

    messages 是聊天应用的核心。
    它不是一个普通字符串，而是一个“消息列表”。

    role 表示这句话是谁说的：
    - system：给模型的身份和规则
    - user：用户说的话
    - assistant：模型之前回答过的话
    """
    return [
        {
            "role": "system",
            "content": (
                "你是一个耐心的中文 AI 学习助手。"
                "请用初学者能听懂的方式回答，尽量简洁、清楚。"
            ),
        }
    ]


def ask_llm(messages: list[dict[str, str]]) -> str:
    """把完整的 messages 发送给大模型，并返回模型回答。

    注意：这里传入的是完整 messages，而不是单独一个 question。
    因为模型想“记住上下文”，就必须看到之前的 user 和 assistant 消息。
    """
    load_config()
    mode = (os.getenv("AI_CHAT_MODE") or "mock").strip().lower()

    if mode == "mock":
        last_user_message = get_last_user_message(messages)
        return (
            "这是 mock 模式下的模拟回答。\n"
            f"你刚才的问题是：{last_user_message}\n\n"
            "mock 模式不会请求真实 API，所以不会消耗额度。\n"
            "它适合用来学习 messages、上下文和程序结构。"
        )

    client = create_client()
    model = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")

    # 这一行是真正向大模型 API 发送请求的地方。
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    # 从 API 返回结果中取出模型的第一条回答文本。
    return response.choices[0].message.content or ""


def summarize_text(text: str) -> str:
    """让大模型总结一段文本。

    这是“文件总结”功能的核心：
    1. 程序先读取文件，得到 text。
    2. 再把 text 放进 user message。
    3. 最后像聊天一样调用大模型 API。

    注意：这里还不是 RAG。
    现在的做法是把整段文本直接发给模型，适合较短的 txt 文件。
    """
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个中文文档总结助手。"
                "请先用 3 句话总结核心内容，"
                "再列出 3 个要点，最后给出一个适合初学者的解释。"
            ),
        },
        {
            "role": "user",
            "content": f"请总结下面这段文本：\n\n{text}",
        },
    ]

    return ask_llm(messages)


def split_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """把长文本切成多个文本块。

    chunk_size 控制每个文本块最多有多少字符。
    overlap 控制相邻文本块之间重复多少字符，用来减少上下文断裂。
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0。")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0。")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size。")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start += step

    return chunks


def score_chunk(query: str, chunk: str) -> int:
    """给一个 chunk 打相关性分数。

    这是为了学习检索流程写的简化版本，不是正式 RAG 的向量检索。
    分数越高，说明这个 chunk 和用户问题越可能相关。
    """
    query = query.strip().lower()
    chunk = chunk.lower()

    if not query or not chunk:
        return 0

    score = 0

    if query in chunk:
        score += 10

    words = query.split()
    if len(words) <= 1:
        words = [char for char in query if char.strip()]

    for word in words:
        if word in chunk:
            score += chunk.count(word)

    return score


def retrieve_chunks(query: str, chunks: list[str], top_k: int = 3) -> list[dict[str, int | str]]:
    """从多个 chunks 里找出和问题最相关的几块。

    这个函数是 RAG 的前置练习：
    1. 用户提出 query。
    2. 程序给每个 chunk 打分。
    3. 返回分数最高的 top_k 个 chunk。
    """
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    scored_chunks = []
    for index, chunk in enumerate(chunks, start=1):
        score = score_chunk(query, chunk)
        if score > 0:
            scored_chunks.append(
                {
                    "index": index,
                    "score": score,
                    "text": chunk,
                }
            )

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return scored_chunks[:top_k]


def tokenize_text(text: str) -> list[str]:
    """把文本拆成用于玩具 embedding 的 token。

    英文会按单词切分，中文会按单个汉字切分。
    这不是生产级分词，只用于帮助理解“文本转向量”的基本思路。
    """
    text = text.lower()
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text)


def create_toy_embedding(text: str) -> dict[str, float]:
    """把文本转换成一个简单词频向量。

    正式 embedding 通常是由模型生成的稠密数字列表。
    这里为了学习，用“token -> 出现次数”模拟一个容易看懂的向量。
    """
    vector: dict[str, float] = {}

    for token in tokenize_text(text):
        vector[token] = vector.get(token, 0.0) + 1.0

    return vector


def cosine_similarity(vector_a: dict[str, float], vector_b: dict[str, float]) -> float:
    """计算两个向量的余弦相似度。

    返回值越接近 1，说明两个向量方向越相似。
    返回值越接近 0，说明两个向量越不相关。
    """
    if not vector_a or not vector_b:
        return 0.0

    common_tokens = set(vector_a) & set(vector_b)
    dot_product = sum(vector_a[token] * vector_b[token] for token in common_tokens)

    length_a = math.sqrt(sum(value * value for value in vector_a.values()))
    length_b = math.sqrt(sum(value * value for value in vector_b.values()))

    if length_a == 0 or length_b == 0:
        return 0.0

    return dot_product / (length_a * length_b)


def retrieve_chunks_by_toy_embedding(
    query: str,
    chunks: list[str],
    top_k: int = 3,
) -> list[dict[str, float | int | str]]:
    """用玩具 embedding 从 chunks 里找相关片段。

    这个函数比关键词计分更接近正式 RAG 的结构：
    1. 把 query 转成向量。
    2. 把每个 chunk 转成向量。
    3. 计算 query 向量和 chunk 向量的相似度。
    4. 返回相似度最高的 top_k 个 chunk。
    """
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    query_vector = create_toy_embedding(query)
    results = []

    for index, chunk in enumerate(chunks, start=1):
        chunk_vector = create_toy_embedding(chunk)
        similarity = cosine_similarity(query_vector, chunk_vector)
        if similarity > 0:
            results.append(
                {
                    "index": index,
                    "score": round(similarity, 4),
                    "text": chunk,
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def build_toy_vector_index(chunks: list[str]) -> list[dict[str, object]]:
    """提前给每个 chunk 计算向量，形成一个很小的内存索引。

    这样同一份文档被反复提问时，不需要每次都重新计算 chunk 向量。
    真实向量库也有类似思想：先把文档向量存起来，查询时只算问题向量。
    """
    index = []

    for chunk_index, chunk in enumerate(chunks, start=1):
        index.append(
            {
                "index": chunk_index,
                "text": chunk,
                "vector": create_toy_embedding(chunk),
            }
        )

    return index


def search_toy_vector_index(
    query: str,
    vector_index: list[dict[str, object]],
    top_k: int = 3,
) -> list[dict[str, float | int | str]]:
    """用已经建好的 chunk 向量索引检索相关片段。"""
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    query_vector = create_toy_embedding(query)
    results = []

    for item in vector_index:
        chunk_vector = item["vector"]
        if not isinstance(chunk_vector, dict):
            continue

        similarity = cosine_similarity(query_vector, chunk_vector)
        if similarity > 0:
            results.append(
                {
                    "index": int(item["index"]),
                    "score": round(similarity, 4),
                    "text": str(item["text"]),
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def dense_cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """计算真实 embedding 这种数字列表之间的余弦相似度。"""
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度不同，不能计算相似度。")

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    length_a = math.sqrt(sum(value * value for value in vector_a))
    length_b = math.sqrt(sum(value * value for value in vector_b))

    if length_a == 0 or length_b == 0:
        return 0.0

    return dot_product / (length_a * length_b)


def retrieve_chunks_by_real_embedding(
    query: str,
    chunks: list[str],
    top_k: int = 3,
) -> list[dict[str, float | int | str]]:
    """用真实 embedding API 从 chunks 里检索相关片段。"""
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    query = query.strip()
    if not query:
        raise ValueError("问题不能为空。")

    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    if not cleaned_chunks:
        return []

    query_vector = create_real_embedding(query)
    chunk_vectors = create_real_embeddings(cleaned_chunks)

    results = []
    for index, (chunk, chunk_vector) in enumerate(
        zip(cleaned_chunks, chunk_vectors),
        start=1,
    ):#把两个列表一一配对并加序号
        similarity = dense_cosine_similarity(query_vector, chunk_vector)
        results.append(
            {
                "index": index,
                "score": round(similarity, 4),
                "text": chunk,
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def build_real_vector_index(chunks: list[str]) -> list[dict[str, object]]:
    """提前给 chunks 生成真实 embedding，形成一个内存里的真实向量索引。"""
    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    if not cleaned_chunks:
        return []

    chunk_vectors = create_real_embeddings(cleaned_chunks)
    vector_index = []

    for chunk_index, (chunk, vector) in enumerate(
        zip(cleaned_chunks, chunk_vectors),
        start=1,
    ):
        vector_index.append(
            {
                "index": chunk_index,
                "text": chunk,
                "vector": vector,
            }
        )

    return vector_index


def search_real_vector_index(
    query: str,
    vector_index: list[dict[str, object]],
    top_k: int = 3,
) -> list[dict[str, float | int | str]]:
    """用已经建好的真实 embedding 索引检索相关片段。"""
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    query = query.strip()
    if not query:
        raise ValueError("问题不能为空。")

    query_vector = create_real_embedding(query)
    results = []

    for item in vector_index:
        chunk_vector = item["vector"]
        if not isinstance(chunk_vector, list):
            continue

        similarity = dense_cosine_similarity(query_vector, chunk_vector)
        results.append(
            {
                "index": int(item["index"]),
                "score": round(similarity, 4),
                "text": str(item["text"]),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def normalize_chroma_collection_name(collection_name: str) -> str:
    """把用户输入的集合名称转换成 Chroma 可以使用的 collection 名称。"""
    collection_name = collection_name.strip()
    if not collection_name:
        raise ValueError("Chroma collection 名称不能为空。")

    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", collection_name)
    safe_name = safe_name.strip("_-") or "doc"

    if len(safe_name) < 3:
        safe_name = f"doc_{safe_name}"

    return safe_name[:63]


def create_chroma_client():
    """创建一个持久化的 Chroma 客户端。"""
    import chromadb

    CHROMA_DB_DIR.mkdir(exist_ok=True)

    """
    CHROMA_DB_DIR	一个变量，表示目录路径（比如 "./chroma_db"）
    .mkdir()	创建这个目录
    exist_ok=True	如果目录已存在，不报错（否则会报错）
    """
    return chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    """
    chromadb.PersistentClient()	创建一个持久化的 Chroma 客户端
    path=str(CHROMA_DB_DIR)	指定数据存储在哪个文件夹
    return	把这个客户端返回给调用方
    """

def save_chunks_to_chroma(
    collection_name: str,
    chunks: list[str],
) -> tuple[str, int]:
    """把 chunks 的真实 embedding 保存到 Chroma。"""
    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    if not cleaned_chunks:
        raise ValueError("没有可保存的 chunk。")

    safe_name = normalize_chroma_collection_name(collection_name)
    client = create_chroma_client()
    collection = client.get_or_create_collection(
        name=safe_name,
        metadata={"hnsw:space": "cosine"},
    )

    embeddings = create_real_embeddings(cleaned_chunks)
    ids = [f"{safe_name}_chunk_{index}" for index in range(1, len(cleaned_chunks) + 1)]
    metadatas = [
        {
            "chunk_index": index,
            "source": safe_name,
        }
        for index in range(1, len(cleaned_chunks) + 1)
    ]

    collection.upsert(
        ids=ids,
        documents=cleaned_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return safe_name, len(cleaned_chunks)


def query_chroma_collection(
    collection_name: str,
    query: str,
    top_k: int = 3,
) -> list[dict[str, float | int | str]]:
    """从 Chroma collection 里检索和问题最相关的 chunks。"""
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    query = query.strip()
    if not query:
        raise ValueError("问题不能为空。")

    safe_name = normalize_chroma_collection_name(collection_name)
    client = create_chroma_client()
    collection = client.get_collection(name=safe_name)

    query_embedding = create_real_embedding(query)
    response = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    results = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        chunk_index = 0
        if isinstance(metadata, dict):
            chunk_index = int(metadata.get("chunk_index", 0))

        results.append(
            {
                "index": chunk_index,
                "score": round(1 - float(distance), 4),
                "text": str(document),
            }
        )

    return results


def answer_with_chroma_rag(
    collection_name: str,
    query: str,
    top_k: int = 3,
    min_score: float = 0.2,
) -> dict[str, object]:
    """完整 RAG：先从 Chroma 检索 chunks，再让 LLM 基于 chunks 回答。"""
    retrieved_chunks = query_chroma_collection(
        collection_name=collection_name,
        query=query,
        top_k=top_k,
    )
    useful_chunks = [
        chunk
        for chunk in retrieved_chunks
        if float(chunk["score"]) >= min_score
    ]

    if not useful_chunks:
        return {
            "answer": (
                "根据当前资料无法确定。\n\n"
                "原因：Chroma 没有检索到相似度足够高的参考片段。"
            ),
            "sources": retrieved_chunks,
        }

    context_parts = []
    for result in useful_chunks:
        context_parts.append(
            f"[chunk {result['index']}，相似度 {result['score']}]\n{result['text']}"
        )

    context = "\n\n".join(context_parts)
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个严谨的中文 RAG 问答助手。"
                "你必须只根据用户提供的参考资料回答。"
                "如果参考资料中没有答案，请明确说“根据当前资料无法确定”。"
                "不要编造参考资料之外的信息。"
                "回答后请列出你使用到的 chunk 编号。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"用户问题：{query}\n\n"
                f"参考资料：\n{context}\n\n"
                "请基于参考资料回答用户问题。"
            ),
        },
    ]

    answer = ask_llm(messages)
    return {
        "answer": answer,
        "sources": useful_chunks,
        "all_retrieved": retrieved_chunks,
    }


def list_chroma_collections() -> list[str]:
    """列出当前 Chroma 数据库里的 collection 名称。"""
    if not CHROMA_DB_DIR.exists():
        return []

    client = create_chroma_client()
    return sorted(collection.name for collection in client.list_collections())


def get_last_user_message(messages: list[dict[str, str]]) -> str:
    """从 messages 里找到最后一条用户消息，主要给 mock 模式使用。"""
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""


def explain_error(error: Exception) -> str:
    """把常见 API 报错翻译成适合初学者看的中文提示。"""
    if isinstance(error, AuthenticationError):
        return (
            "认证失败：API key 可能填错了，或者这个 key 没有权限。\n"
            "请检查 .env 里的 DEEPSEEK_API_KEY。"
        )

    if isinstance(error, RateLimitError):
        return (
            "请求被限制：可能是请求太频繁、额度不足，或者账号没有可用余额。\n"
            "请检查你的 API 账号额度。"
        )

    if isinstance(error, BadRequestError):
        return (
            "请求参数有问题：常见原因是模型名写错，或者当前账号不能使用这个模型。\n"
            "请检查 .env 里的 OPENAI_MODEL。"
        )

    if isinstance(error, APIConnectionError):
        return (
            "网络连接失败：程序没有连上大模型 API 服务。\n"
            "请检查网络，或者检查 .env 里的 OPENAI_BASE_URL。"
        )

    if isinstance(error, APIStatusError):
        if error.status_code == 402:
            return (
                "API 服务返回 402：账号余额不足。\n"
                "这不是 Python 语法问题，而是 API 账号需要充值或领取额度。"
            )

        return (
            f"API 服务返回错误，状态码：{error.status_code}\n"
            "这通常不是 Python 语法问题，而是 API 服务、账号、模型或请求参数的问题。"
        )

    if isinstance(error, OpenAIError):
        return (
            "OpenAI SDK 报错。\n"
            "这说明代码已经走到 API 请求阶段了，问题通常在 key、模型名、网络或服务配置。"
        )

    if isinstance(error, (RuntimeError, ValueError)):
        return str(error)

    return "程序运行时出现未知错误。"


def run_one_question(question: str) -> None:
    """只问一次问题，适合命令行传参或快速测试。"""
    messages = create_initial_messages()
    messages.append({"role": "user", "content": question})

    answer = ask_llm(messages)
    print()
    print("AI：")
    print(answer)


def run_chat_loop() -> None:
    """连续聊天模式。

    重点逻辑：
    1. 程序开始时创建 messages。
    2. 用户每输入一句话，就把它 append 到 messages。
    3. 模型回答后，也把回答 append 到 messages。
    4. 下一轮请求时，完整 messages 会再次发送给模型。

    所以模型看起来像“记得前面聊过什么”。
    """
    messages = create_initial_messages()

    print("AI 入门聊天程序")
    print("输入问题后按回车。输入“退出”结束聊天。")
    print()

    while True:
        question = input("你：").strip()

        if not question:
            print("请输入一个问题，或者输入“退出”。")
            continue

        if question in {"退出", "exit", "quit"}:
            print("聊天结束。")
            break

        # 把用户这一轮的问题加入历史消息。
        messages.append({"role": "user", "content": question})

        try:
            answer = ask_llm(messages)
        except Exception as error:
            print()
            print("运行失败，但这不是坏事：你已经走到真实 API 调用这一步了。")
            print()
            print(explain_error(error))
            print()
            print("原始错误信息：")
            print(repr(error))
            break

        print()
        print("AI：")
        print(answer)
        print()

        # 把模型这一轮的回答也加入历史消息。
        # 下一次调用 API 时，模型就能看到这条回答。
        messages.append({"role": "assistant", "content": answer})


def main() -> None:
    parser = argparse.ArgumentParser(description="最小 AI 聊天程序")
    parser.add_argument(
        "--question",
        "-q",
        help='直接传入一个问题，例如：python main.py --question "什么是 AI 应用开发？"',
    )
    args = parser.parse_args()

    if args.question:
        question = args.question.strip()
        if not question:
            print("问题不能为空。")
            return

        print("AI 入门聊天程序")
        print(f"你：{question}")

        try:
            run_one_question(question)
        except Exception as error:
            print()
            print("运行失败，但这不是坏事：你已经走到真实 API 调用这一步了。")
            print()
            print(explain_error(error))
            print()
            print("原始错误信息：")
            print(repr(error))
        return

    run_chat_loop()


if __name__ == "__main__":
    main()

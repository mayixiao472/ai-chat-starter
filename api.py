from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel#定义数据格式（JSON长什么样）

from database import insert_document_record, list_document_records
from main import (
    answer_with_chroma_rag,
    ask_llm,
    create_initial_messages,
    explain_error,
    save_chunks_to_chroma,
    split_text,
    summarize_text,
)


app = FastAPI(
    title="AI Chat Starter API",
    description="第二阶段学习用的 FastAPI 后端入口。",
    version="0.1.0",
)


class EchoRequest(BaseModel):#前端给我的JSON，FastAPI 会自动把 JSON 塞进 EchoRequest
    """POST /echo 的请求体。

    BaseModel 可以理解成“规定前端传来的 JSON 应该长什么样”。
    """

    message: str


class EchoResponse(BaseModel):#返回给前端的 JSON 结构。
    """POST /echo 的响应体。"""

    message: str
    length: int


class ChatRequest(BaseModel):
    """POST /chat 的请求体。"""

    question: str


class ChatResponse(BaseModel):
    """POST /chat 的响应体。"""

    answer: str


class SummarizeRequest(BaseModel):
    """POST /summarize 的请求体。"""

    text: str


class SummarizeResponse(BaseModel):
    """POST /summarize 的响应体。"""

    summary: str


class DocumentUploadResponse(BaseModel):
    """POST /documents 的响应体。"""

    id: int | None = None
    filename: str
    collection_name: str
    chunk_count: int
    indexed_count: int


class SourceChunk(BaseModel):
    """RAG 回答引用到的 chunk。"""

    index: int
    score: float
    text: str


class AskDocRequest(BaseModel):
    """POST /ask-doc 的请求体。"""

    collection_name: str
    question: str
    top_k: int = 3
    min_score: float = 0.2


class AskDocResponse(BaseModel):
    """POST /ask-doc 的响应体。"""

    answer: str
    sources: list[SourceChunk]


class DocumentRecord(BaseModel):
    """GET /documents 返回的一条文档记录。"""

    id: int
    filename: str
    collection_name: str
    chunk_count: int
    indexed_count: int
    created_at: str


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查接口。

    GET 通常用于读取信息。
    这个接口不需要请求体，只是告诉调用者：后端服务还活着。
    """
    return {
        "status": "ok",
        "service": "ai-chat-starter-api",
    }


@app.post("/echo", response_model=EchoResponse)
def echo(request: EchoRequest) -> EchoResponse:
    """回声接口。

    POST 通常用于提交数据。
    这个接口会接收一段 JSON，再把内容原样返回，方便你理解请求体和响应体。
    """
    return EchoResponse(
        message=request.message,
        length=len(request.message),
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """聊天接口。

    前端传入一个 question，后端复用 main.py 里的 ask_llm 调用大模型。
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=400,
            detail="question 不能为空。",
        )

    messages = create_initial_messages()
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    try:
        answer = ask_llm(messages)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=explain_error(error),
        ) from error

    return ChatResponse(answer=answer)


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """文本总结接口。

    前端传入一段 text，后端复用 main.py 里的 summarize_text 生成总结。
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="text 不能为空。",
        )

    try:
        summary = summarize_text(text)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=explain_error(error),
        ) from error

    return SummarizeResponse(summary=summary)


@app.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),#...表示这个参数file为必填项
    collection_name: str = Form(""),
    chunk_size: int = Form(500),
    overlap: int = Form(100),
    max_chunks: int = Form(20),
) -> DocumentUploadResponse:
    """文档上传接口。

    上传 txt 文件后，后端会切分文本，并把 chunks 写入 Chroma。
    """
    filename = file.filename or "uploaded.txt"
    if not filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="目前只支持上传 .txt 文件。",
        )

    if max_chunks <= 0:
        raise HTTPException(
            status_code=400,
            detail="max_chunks 必须大于 0。",
        )

    try:
        file_bytes = await file.read()
        text = file_bytes.decode("utf-8", errors="ignore").strip()
        if not text:
            raise ValueError("文件内容不能为空。")

        chunks = split_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        chunks_for_chroma = chunks[:max_chunks]

        final_collection_name = collection_name.strip()
        if not final_collection_name:
            final_collection_name = Path(filename).stem

        saved_name, indexed_count = save_chunks_to_chroma(
            final_collection_name,
            chunks_for_chroma,
        )
        document_id = insert_document_record(
            filename=filename,
            collection_name=saved_name,
            chunk_count=len(chunks),
            indexed_count=indexed_count,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=explain_error(error),
        ) from error

    return DocumentUploadResponse(
        id=document_id,
        filename=filename,
        collection_name=saved_name,
        chunk_count=len(chunks),
        indexed_count=indexed_count,
    )


@app.get("/documents", response_model=list[DocumentRecord])
def list_documents() -> list[DocumentRecord]:
    """查询已经上传过的文档记录。"""
    try:
        records = list_document_records()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=explain_error(error),
        ) from error

    return [
        DocumentRecord(
            id=int(record["id"]),
            filename=str(record["filename"]),
            collection_name=str(record["collection_name"]),
            chunk_count=int(record["chunk_count"]),
            indexed_count=int(record["indexed_count"]),
            created_at=str(record["created_at"]),
        )
        for record in records
    ]


@app.post("/ask-doc", response_model=AskDocResponse)
def ask_document(request: AskDocRequest) -> AskDocResponse:
    """文档问答接口。

    根据 collection_name 从 Chroma 检索资料，再调用 LLM 生成回答。
    """
    collection_name = request.collection_name.strip()
    question = request.question.strip()

    if not collection_name:
        raise HTTPException(
            status_code=400,
            detail="collection_name 不能为空。",
        )

    if not question:
        raise HTTPException(
            status_code=400,
            detail="question 不能为空。",
        )

    if request.top_k <= 0:
        raise HTTPException(
            status_code=400,
            detail="top_k 必须大于 0。",
        )

    if not 0 <= request.min_score <= 1:
        raise HTTPException(
            status_code=400,
            detail="min_score 必须在 0 到 1 之间。",
        )

    try:
        rag_result = answer_with_chroma_rag(
            collection_name=collection_name,
            query=question,
            top_k=request.top_k,
            min_score=request.min_score,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=explain_error(error),
        ) from error

    sources = [
        SourceChunk(
            index=int(source["index"]),
            score=float(source["score"]),
            text=str(source["text"]),
        )
        for source in rag_result["sources"]
    ]

    return AskDocResponse(
        answer=str(rag_result["answer"]),
        sources=sources,
    )

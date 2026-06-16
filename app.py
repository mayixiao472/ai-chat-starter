import streamlit as st

from main import (
    answer_with_chroma_rag,
    ask_llm,
    build_real_vector_index,
    build_toy_vector_index,
    create_initial_messages,
    create_real_embedding,
    explain_error,
    list_chroma_collections,
    query_chroma_collection,
    retrieve_chunks,
    save_chunks_to_chroma,
    search_real_vector_index,
    search_toy_vector_index,
    split_text,
    summarize_text,
)


st.set_page_config(
    page_title="AI 聊天入门",
    page_icon="AI",
)

st.title("AI 聊天入门")


def reset_chat() -> None:
    """重置聊天记录。

    Streamlit 每次交互都会重新运行整个 app.py。
    所以历史对话不能只放在普通变量里，需要放进 st.session_state。
    """
    st.session_state.messages = create_initial_messages()


@st.cache_data
def build_cached_toy_vector_index(
    text: str,
    chunk_size: int,
    overlap: int,
) -> tuple[list[str], list[dict[str, object]]]:
    """缓存同一份文本的 chunks 和玩具向量索引。

    Streamlit 每次交互都会重新运行 app.py。
    加上 st.cache_data 后，只要 text、chunk_size、overlap 不变，
    Streamlit 就会复用上一次的切分结果和 chunk 向量。
    """
    chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)
    vector_index = build_toy_vector_index(chunks)
    return chunks, vector_index


@st.cache_data
def build_cached_real_vector_index(
    text: str,
    chunk_size: int,
    overlap: int,
    max_chunks: int,
) -> tuple[list[str], list[dict[str, object]]]:
    """缓存同一份文本的真实 embedding 索引，避免反复消耗 API。"""
    chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)
    chunks_for_index = chunks[:max_chunks]
    """
    真实项目里一般不会这么粗暴地只取前max_chunks个，而是会：
    第一次上传文档时，把全部 chunks 都向量化
    然后存进 Chroma / FAISS / 数据库
    之后每次提问都复用这些向量
    """
    vector_index = build_real_vector_index(chunks_for_index)
    return chunks, vector_index


# 第一次打开网页时，初始化 messages。
if "messages" not in st.session_state:
    reset_chat()


(
    chat_tab,
    summary_tab,
    split_tab,
    retrieval_tab,
    embedding_tab,
    real_embedding_tab,
    real_retrieval_tab,
    chroma_tab,
) = st.tabs(
    [
        "聊天",
        "文本总结",
        "文本切分",
        "简单检索",
        "向量相似度",
        "真实 embedding API",
        "真实向量检索",
        "Chroma 向量库",
    ]
)


with chat_tab:          #这种with开头的代码 主要是 Streamlit 用法
    with st.sidebar:
        st.header("控制")
        if st.button("清空对话"):
            reset_chat()
            st.rerun()

        st.caption("这只是网页入口，真正调用模型的逻辑仍然在 main.py 里。")

    # 显示历史对话。
    # system message 是给模型看的规则，不需要展示给用户。
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # chat_input 会在页面底部显示一个聊天输入框。
    question = st.chat_input("输入你的问题")

    if question:
        # 1. 把用户输入加入 messages。
        st.session_state.messages.append({"role": "user", "content": question})

        # 2. 立刻把用户输入显示在页面上。
        with st.chat_message("user"):
            st.write(question)

        # 3. 把完整 messages 发给大模型。
        with st.chat_message("assistant"):
            with st.spinner("AI 正在思考..."):
                try:
                    answer = ask_llm(st.session_state.messages)
                except Exception as error:
                    answer = (
                        "运行失败。\n\n"
                        f"{explain_error(error)}\n\n"
                        f"原始错误信息：{repr(error)}"
                    )

                st.write(answer)

        # 4. 把模型回答也加入 messages。
        # 下一轮提问时，模型就能看到之前的对话。
        st.session_state.messages.append({"role": "assistant", "content": answer})


with summary_tab:
    st.subheader("上传 txt 文件")

    uploaded_file = st.file_uploader(
        "选择一个 .txt 文件",
        type=["txt"],
    )

    if uploaded_file is not None:
        # uploaded_file.read() 读出来的是 bytes，需要 decode 成中文字符串。
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        text = text.strip()

        st.write(f"文件名：{uploaded_file.name}")
        st.write(f"文本长度：{len(text)} 个字符")

        # 现在先限制长度，避免一次发太多内容导致慢、贵或超过模型上下文。
        max_chars = 6000
        if len(text) > max_chars:
            st.warning(f"文本较长，本次只总结前 {max_chars} 个字符。")
            text_for_summary = text[:max_chars]
        else:
            text_for_summary = text

        with st.expander("查看读取到的文本"):
            st.write(text_for_summary)

        if st.button("总结这个文件"):
            if not text_for_summary:
                st.warning("文件内容为空，无法总结。")
            else:
                with st.spinner("AI 正在总结..."):
                    try:
                        summary = summarize_text(text_for_summary)
                    except Exception as error:
                        summary = (
                            "总结失败。\n\n"
                            f"{explain_error(error)}\n\n"
                            f"原始错误信息：{repr(error)}"
                        )

                st.subheader("总结结果")
                st.write(summary)


with split_tab:
    st.subheader("文本切分预览")

    split_file = st.file_uploader(
        "选择一个 .txt 文件进行切分",
        type=["txt"],
        key="split_file",
    )

    chunk_size = st.number_input(
        "每个 chunk 的最大字符数",
        min_value=50,
        max_value=3000,
        value=500,
        step=50,
    )
    overlap = st.number_input(
        "相邻 chunk 重叠字符数",
        min_value=0,
        max_value=1000,
        value=100,
        step=50,
    )

    if split_file is not None:
        split_text_content = split_file.read().decode("utf-8", errors="ignore")
        split_text_content = split_text_content.strip()

        st.write(f"文件名：{split_file.name}")
        st.write(f"原文长度：{len(split_text_content)} 个字符")

        try:
            chunks = split_text(
                split_text_content,
                chunk_size=int(chunk_size),
                overlap=int(overlap),
            )
        except ValueError as error:
            st.warning(str(error))
        else:
            st.write(f"切分结果：共 {len(chunks)} 个 chunk")

            for index, chunk in enumerate(chunks, start=1):
                with st.expander(f"chunk {index}：{len(chunk)} 个字符"):
                    st.write(chunk)


with retrieval_tab:
    st.subheader("从 chunks 里检索相关片段")

    retrieval_file = st.file_uploader(
        "选择一个 .txt 文件进行检索",
        type=["txt"],
        key="retrieval_file",
    )

    query = st.text_input("输入一个问题或关键词")

    retrieval_chunk_size = st.number_input(
        "检索用 chunk 最大字符数",
        min_value=50,
        max_value=3000,
        value=500,
        step=50,
    )
    retrieval_overlap = st.number_input(
        "检索用 chunk 重叠字符数",
        min_value=0,
        max_value=1000,
        value=100,
        step=50,
    )
    top_k = st.number_input(
        "返回最相关的 chunk 数量",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    if retrieval_file is not None and query:
        retrieval_text = retrieval_file.read().decode("utf-8", errors="ignore")
        retrieval_text = retrieval_text.strip()

        try:
            chunks = split_text(
                retrieval_text,
                chunk_size=int(retrieval_chunk_size),
                overlap=int(retrieval_overlap),
            )
            results = retrieve_chunks(query, chunks, top_k=int(top_k))
        except ValueError as error:
            st.warning(str(error))
        else:
            st.write(f"原文共切成 {len(chunks)} 个 chunk")

            if not results:
                st.warning("没有检索到相关 chunk。可以换一个关键词试试。")
            else:
                st.write(f"找到 {len(results)} 个相关 chunk")

                for result in results:
                    with st.expander(
                        f"chunk {result['index']}，相关分数：{result['score']}"
                    ):
                        st.write(result["text"])


with embedding_tab:
    st.subheader("玩具 embedding 相似度检索")

    embedding_file = st.file_uploader(
        "选择一个 .txt 文件进行向量相似度检索",
        type=["txt"],
        key="embedding_file",
    )

    embedding_query = st.text_input("输入问题", key="embedding_query")

    embedding_chunk_size = st.number_input(
        "向量检索用 chunk 最大字符数",
        min_value=50,
        max_value=3000,
        value=500,
        step=50,
    )
    embedding_overlap = st.number_input(
        "向量检索用 chunk 重叠字符数",
        min_value=0,
        max_value=1000,
        value=100,
        step=50,
    )
    embedding_top_k = st.number_input(
        "向量检索返回 chunk 数量",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    st.caption("这里用的是教学用的词频向量，不是真正的生产级 embedding。")

    if embedding_file is not None and embedding_query:
        embedding_text = embedding_file.read().decode("utf-8", errors="ignore")
        embedding_text = embedding_text.strip()

        try:
            chunks, vector_index = build_cached_toy_vector_index(
                embedding_text,
                int(embedding_chunk_size),
                int(embedding_overlap),
            )
            results = search_toy_vector_index(
                embedding_query,
                vector_index,
                top_k=int(embedding_top_k),
            )
        except ValueError as error:
            st.warning(str(error))
        else:
            st.write(f"原文共切成 {len(chunks)} 个 chunk")
            st.write(f"已为 {len(vector_index)} 个 chunk 建立缓存向量索引")

            if not results:
                st.warning("没有找到相似 chunk。可以换一个更接近原文的问法。")
            else:
                st.write(f"找到 {len(results)} 个相似 chunk")

                for result in results:
                    with st.expander(
                        f"chunk {result['index']}，余弦相似度：{result['score']}"
                    ):
                        st.write(result["text"])


with chroma_tab:
    st.subheader("Chroma 向量库")

    collection_name = st.text_input(
        "Collection 名称",
        value="my_first_doc",
        key="collection_name",
    )

    chroma_file = st.file_uploader(
        "选择一个 .txt 文件，保存到 Chroma",
        type=["txt"],
        key="chroma_file",
    )

    chroma_chunk_size = st.number_input(
        "Chroma 入库用 chunk 最大字符数",
        min_value=50,
        max_value=2000,
        value=500,
        step=50,
    )
    chroma_overlap = st.number_input(
        "Chroma 入库用 chunk 重叠字符数",
        min_value=0,
        max_value=800,
        value=100,
        step=50,
    )
    chroma_max_chunks = st.number_input(
        "本次最多入库多少个 chunk",
        min_value=1,
        max_value=50,
        value=8,
        step=1,
    )

    if st.button("生成 embedding 并保存到 Chroma"):
        if chroma_file is None:
            st.warning("请先上传一个 .txt 文件。")
        else:
            chroma_text = chroma_file.read().decode("utf-8", errors="ignore").strip()

            with st.spinner("正在生成真实 embedding，并写入 Chroma..."):
                try:
                    chunks = split_text(
                        chroma_text,
                        chunk_size=int(chroma_chunk_size),
                        overlap=int(chroma_overlap),
                    )
                    chunks_for_chroma = chunks[: int(chroma_max_chunks)]
                    saved_name, saved_count = save_chunks_to_chroma(
                        collection_name,
                        chunks_for_chroma,
                    )
                except Exception as error:
                    st.error("保存到 Chroma 失败。")
                    st.write(explain_error(error))
                    st.write(f"原始错误信息：{repr(error)}")
                else:
                    st.success("已经保存到 Chroma。")
                    st.write(f"Collection：{saved_name}")
                    st.write(f"原文共切成 {len(chunks)} 个 chunk")
                    st.write(f"实际入库 {saved_count} 个 chunk")

    collections = list_chroma_collections()

    if collections:
        selected_collection = st.selectbox(
            "选择一个 Chroma collection",
            collections,
        )
        chroma_query = st.text_input(
            "输入问题，从 Chroma 中检索",
            key="chroma_query",
        )
        chroma_top_k = st.number_input(
            "Chroma 返回 chunk 数量",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
        )
        rag_min_score = st.slider(
            "RAG 最低引用相似度",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
        )

        if st.button("检索 Chroma"):
            with st.spinner("正在从 Chroma 检索..."):
                try:
                    results = query_chroma_collection(
                        selected_collection,
                        chroma_query,
                        top_k=int(chroma_top_k),
                    )
                except Exception as error:
                    st.error("检索 Chroma 失败。")
                    st.write(explain_error(error))
                    st.write(f"原始错误信息：{repr(error)}")
                else:
                    if not results:
                        st.warning("没有找到相似 chunk。")
                    else:
                        st.write(f"找到 {len(results)} 个相似 chunk")

                        for result in results:
                            with st.expander(
                                f"chunk {result['index']}，相似度：{result['score']}"
                            ):
                                st.write(result["text"])

        if st.button("生成 RAG 回答"):
            with st.spinner("正在检索资料并调用 LLM 生成回答..."):
                try:
                    rag_result = answer_with_chroma_rag(
                        selected_collection,
                        chroma_query,
                        top_k=int(chroma_top_k),
                        min_score=float(rag_min_score),
                    )
                except Exception as error:
                    st.error("生成 RAG 回答失败。")
                    st.write(explain_error(error))
                    st.write(f"原始错误信息：{repr(error)}")
                else:
                    st.subheader("RAG 回答")
                    st.write(rag_result["answer"])

                    sources = rag_result["sources"]
                    if sources:
                        st.subheader("引用来源")
                        for source in sources:
                            with st.expander(
                                f"chunk {source['index']}，相似度：{source['score']}"
                            ):
                                st.write(source["text"])
                    else:
                        st.warning("没有达到最低相似度阈值的引用来源。")
    else:
        st.info("还没有 Chroma collection。请先上传 txt 并保存到 Chroma。")


with real_embedding_tab:
    st.subheader("真实 embedding API")

    embedding_text_input = st.text_area(
        "输入一段文本",
        value="我正在学习 AI 应用开发。",
        height=120,
    )

    if st.button("生成真实 embedding"):
        with st.spinner("正在调用 embedding API..."):
            try:
                embedding = create_real_embedding(embedding_text_input)
            except Exception as error:
                st.error("生成 embedding 失败。")
                st.write(explain_error(error))
                st.write(f"原始错误信息：{repr(error)}")
            else:
                st.write(f"向量维度：{len(embedding)}")
                st.write("前 10 个向量值：")
                st.write(embedding[:10])


with real_retrieval_tab:
    st.subheader("真实 embedding 检索")

    real_retrieval_file = st.file_uploader(
        "选择一个 .txt 文件，用真实 embedding 检索相关片段",
        type=["txt"],
        key="real_retrieval_file",
    )

    real_retrieval_query = st.text_input(
        "输入问题",
        key="real_retrieval_query",
    )

    real_retrieval_chunk_size = st.number_input(
        "真实向量检索用 chunk 最大字符数",
        min_value=50,
        max_value=2000,
        value=500,
        step=50,
    )
    real_retrieval_overlap = st.number_input(
        "真实向量检索用 chunk 重叠字符数",
        min_value=0,
        max_value=800,
        value=100,
        step=50,
    )
    real_retrieval_top_k = st.number_input(
        "真实向量检索返回 chunk 数量",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )
    max_real_chunks = st.number_input(
        "本次最多向量化多少个 chunk",
        min_value=1,
        max_value=30,
        value=8,
        step=1,
    )

    st.caption(
        "这一步会真实调用 embedding API。为了避免一次请求太多文本，页面会限制本次向量化的 chunk 数量。"
    )

    if real_retrieval_file is not None and real_retrieval_query:
        real_retrieval_text = real_retrieval_file.read().decode("utf-8", errors="ignore")
        real_retrieval_text = real_retrieval_text.strip()

        try:
            chunks, vector_index = build_cached_real_vector_index(
                real_retrieval_text,
                chunk_size=int(real_retrieval_chunk_size),
                overlap=int(real_retrieval_overlap),
                max_chunks=int(max_real_chunks),
            )
            results = search_real_vector_index(
                real_retrieval_query,
                vector_index,
                top_k=int(real_retrieval_top_k),
            )
        except Exception as error:
            st.error("真实 embedding 检索失败。")
            st.write(explain_error(error))
            st.write(f"原始错误信息：{repr(error)}")
        else:
            st.write(f"原文共切成 {len(chunks)} 个 chunk")
            st.write(f"已缓存 {len(vector_index)} 个真实 chunk 向量")

            if len(chunks) > len(vector_index):
                st.warning(
                    "为了控制 API 消耗，本次只检索了前面一部分 chunk。可以调大上面的数量继续测试。"
                )

            if not results:
                st.warning("没有找到相似 chunk。")
            else:
                st.write(f"找到 {len(results)} 个相似 chunk")

                for result in results:
                    with st.expander(
                        f"chunk {result['index']}，余弦相似度：{result['score']}"
                    ):
                        st.write(result["text"])

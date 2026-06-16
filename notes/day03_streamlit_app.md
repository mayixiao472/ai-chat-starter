# Day 3：从命令行程序到 Streamlit 网页

今天的目标不是学习复杂前端，而是理解一件事：

```text
同一套 AI 调用逻辑，既可以被 main.py 命令行使用，也可以被 app.py 网页使用。
```

## 1. 为什么需要 app.py

`main.py` 是命令行入口：

```text
你在终端输入问题 -> 程序调用模型 -> 终端打印回答
```

`app.py` 是网页入口：

```text
你在网页输入问题 -> 程序调用模型 -> 网页显示回答
```

真正调用模型的核心函数仍然在 `main.py` 里，比如：

- `ask_llm`
- `create_initial_messages`
- `explain_error`
- `summarize_text`

所以 `app.py` 开头会写：

```python
from main import ask_llm, create_initial_messages, explain_error, summarize_text
```

这行代码的意思是：网页页面不重新写一遍 AI 逻辑，而是复用 `main.py` 里的函数。

## 2. Streamlit 为什么不能直接点运行

普通 Python 文件可以这样运行：

```powershell
python main.py
```

但是 Streamlit 页面要这样运行：

```powershell
python -m streamlit run app.py
```

原因是：`app.py` 不是普通脚本，而是一个 Streamlit 应用页面。

Streamlit 需要先启动一个本地网页服务，然后浏览器才能打开页面。

可以理解成：

```text
streamlit run app.py
-> 启动本地网页服务
-> 读取 app.py
-> 把 st.title、st.button、st.chat_input 等内容变成网页
```

## 3. 页面标题在哪里设置

在 `app.py` 里：

```python
st.set_page_config(
    page_title="AI 聊天入门",
    page_icon="AI",
)

st.title("AI 聊天入门")
```

`st.set_page_config` 设置浏览器标签页信息。

`st.title` 是页面里真正显示出来的大标题。

## 4. 为什么需要 st.session_state

Streamlit 有一个重要特点：

```text
用户每点一次按钮、输入一次内容，app.py 都会从头重新运行。
```

如果聊天记录只放在普通变量里，页面一刷新就没了。

所以代码使用：

```python
st.session_state.messages
```

它可以在页面交互之间保存数据。

在这个项目里，它保存的是聊天历史：

```text
system message
user message
assistant message
user message
assistant message
...
```

## 5. 聊天功能的数据流

聊天页最核心的数据流是：

```text
用户在网页输入问题
-> st.chat_input 得到 question
-> question 被加入 st.session_state.messages
-> ask_llm(messages) 调用模型
-> 页面显示回答
-> 回答也加入 st.session_state.messages
```

对应代码：

```python
question = st.chat_input("输入你的问题")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    answer = ask_llm(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
```

这就是网页聊天的核心逻辑。

## 6. 文件总结功能的数据流

文件总结页最核心的数据流是：

```text
用户上传 txt 文件
-> uploaded_file.read() 读取文件内容
-> decode 把 bytes 转成字符串
-> summarize_text(text) 构造总结 prompt
-> ask_llm(messages) 调用模型
-> 页面显示总结结果
```

对应代码：

```python
text = uploaded_file.read().decode("utf-8", errors="ignore")
summary = summarize_text(text_for_summary)
```

注意：`uploaded_file.read()` 读出来的不是普通中文字符串，而是 `bytes`。

所以要用：

```python
decode("utf-8", errors="ignore")
```

把它转换成 Python 能处理的文本。

## 7. 为什么要限制 max_chars

代码里有：

```python
max_chars = 6000
```

这是为了避免一次把太长的文章发给模型。

原因有三个：

- 太长会变慢
- 太长会更贵
- 太长可能超过模型上下文长度

现在这个功能还不是 RAG。

它只是：

```text
把一段较短文本直接发给模型总结
```

等后面学习 RAG 时，我们会改成：

```text
长文档 -> 切成小块 -> 检索相关内容 -> 再交给模型回答
```

## 8. 今天你要能讲清楚

请用自己的话回答：

1. `app.py` 和 `main.py` 分别负责什么？
2. 为什么 `app.py` 要用 `streamlit run` 启动？
3. `st.session_state.messages` 保存了什么？
4. 用户在网页输入一句话后，代码经过了哪几步？
5. 上传 `.txt` 文件后，为什么要 `decode`？
6. 为什么现在的文件总结还不是 RAG？

## 9. 今天的运行命令

在项目目录里运行：

```powershell
python -m streamlit run app.py
```

打开网页后，做两个测试：

1. 在“聊天”页问：`用三句话解释什么是 RESTful API`
2. 在“文本总结”页上传一个 `.txt` 文件，点击“总结这个文件”

如果这两个测试都能跑通，说明你已经完成了从命令行 AI 程序到网页 AI Demo 的第一步。

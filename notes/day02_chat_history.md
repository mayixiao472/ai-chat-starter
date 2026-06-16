# Day 2：历史对话和上下文

今天的目标是理解一个聊天 AI 为什么看起来像“记得前面说过什么”。

先记住一句话：

```text
模型本身不会自动记住你们之前聊过什么。
程序每次请求时，把历史对话一起放进 messages 发给模型，模型才像是有记忆。
```

## 1. 模型每次只看到本次请求

当你调用大模型 API 时，模型不会主动去你的电脑里找历史记录。

它只能看到这一次请求里传给它的内容。

所以如果你只发送最后一个问题：

```python
messages = [
    {"role": "user", "content": "她叫什么名字？"}
]
```

模型可能不知道“她”是谁。

如果你把前面的对话也发过去：

```python
messages = [
    {"role": "system", "content": "你是一个耐心的中文 AI 学习助手。"},
    {"role": "user", "content": "我给我的项目起名叫 ai-chat-starter。"},
    {"role": "assistant", "content": "这个名字很适合入门 AI 聊天项目。"},
    {"role": "user", "content": "她叫什么名字？"}
]
```

模型才更可能知道“她”指的是 `ai-chat-starter` 这个项目。

## 2. messages 是聊天上下文

`messages` 不是只保存最后一个问题。

它保存的是一段对话历史：

```text
system：规则和身份
user：用户说的话
assistant：模型之前的回答
user：用户的新问题
assistant：模型的新回答
...
```

在你的 `main.py` 里，连续聊天模式大概是这样工作的：

```python
messages = create_initial_messages()

messages.append({"role": "user", "content": question})
answer = ask_llm(messages)
messages.append({"role": "assistant", "content": answer})
```

重点是：

```text
用户问题要 append 进去。
模型回答也要 append 进去。
下一轮再把完整 messages 发给模型。
```

## 3. 模型会不会只回答最后一个问题

通常它会围绕最后一个 `user` message 回答。

但是它不是只看最后一个问题。

更准确的理解是：

```text
最后一个 user message 是当前任务。
前面的 messages 是上下文背景。
```

比如：

```text
前面说：我正在学 Streamlit。
最后问：这个怎么运行？
```

模型会结合前文理解“这个”可能指的是 Streamlit 项目。

## 4. 为什么历史会越来越长

每一轮对话都会增加两条消息：

```text
user message
assistant message
```

所以对话越久，`messages` 越长。

这会带来三个问题：

- 请求变慢
- 消耗更多 token
- 可能超过模型上下文长度

这里的 token 可以先粗略理解成：

```text
模型处理文本时使用的计量单位。
文本越长，token 越多。
```

## 5. 以后怎么处理过长历史

真实项目里不会无限保存全部历史。

常见做法有三种：

### 方法一：只保留最近几轮

比如只保留最近 5 轮对话：

```text
system message
最近 5 个 user/assistant 对话对
```

优点：简单。

缺点：太早的内容会忘掉。

### 方法二：把旧对话总结成摘要

比如：

```text
system message
历史摘要：用户正在学习 AI 应用开发，项目叫 ai-chat-starter，已经学过 API、messages、Streamlit。
最近几轮原始对话
```

优点：能保留长期信息。

缺点：摘要可能丢细节。

### 方法三：重要信息存数据库

比如保存：

- 用户偏好
- 项目名称
- 常用配置
- 长期学习进度

需要时再取出来放进 prompt。

这就是后面学数据库、RAG、记忆系统时会遇到的内容。

## 6. 命令行和网页的区别

在 `main.py` 的连续聊天里，历史保存在普通变量：

```python
messages = create_initial_messages()
```

只要程序不退出，这个变量就还在。

但是在 Streamlit 里，页面每次交互都会重新运行 `app.py`。

所以网页版本要用：

```python
st.session_state.messages
```

它的作用是：

```text
在网页多次交互之间保存 messages。
```

## 7. 今天你要能讲清楚

请用自己的话回答：

1. 为什么模型不是自动记住历史？
2. `messages` 里为什么要放 assistant 之前的回答？
3. 模型是不是只看最后一个问题？
4. 历史对话越来越长会有什么问题？
5. 真实项目里可以怎么控制历史长度？
6. `main.py` 和 `app.py` 保存历史的方式有什么区别？

## 8. 今天的练习

运行命令行连续聊天：

```powershell
python main.py
```

然后连续输入：

```text
我正在做一个 AI 入门项目，项目名叫 ai-chat-starter。
这个项目名是什么意思？
那它适合写进简历吗？
```

观察第三个问题里，“它”没有明确说项目名，但模型仍然可能知道你在问 `ai-chat-starter`。

原因不是模型本地记住了你，而是程序把前面的 `messages` 又一起发给了模型。


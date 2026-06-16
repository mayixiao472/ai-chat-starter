# Day 1：最小 LLM 应用

今天你要学习的是最小但有用的 AI 应用流程：

```text
用户问题 -> messages -> API 调用 -> 模型回答
```

## 核心概念

### API

API 可以理解成：一个程序请求另一个服务帮它做事的方式。

在这个项目里，你的 Python 程序会请求大模型服务生成回答。

### API Key

API key 用来证明这个请求来自你的账号。

不要把 API key 直接写在 Python 代码里。应该把它放在 `.env` 文件中。

### Prompt

Prompt 是你发给模型的指令或问题。

在聊天类 API 里，prompt 通常会被组织成一个 messages 列表。

### role / content

每条 message 通常有两个重要字段：

- `role`：谁在说话
- `content`：说了什么内容

常见 role：

- `system`：设定 AI 助手的行为风格
- `user`：用户的问题
- `assistant`：模型之前的回答

### 为什么模型不是本地运行

这个入门项目不会在你的电脑本地运行大模型。

你的代码会把文本发送给在线的大模型 API，然后 API 把生成的文本返回给你。

## 阅读代码

打开 `main.py`，找到下面这些部分：

- 哪里加载了 `.env`
- 哪里读取了 API key
- 哪里创建了 `messages`
- 哪里发送了 API 请求
- 哪里取出了模型回答

## 你的练习

运行项目，然后输入：

```text
用三句话解释什么是 AI 应用开发
```

然后修改 `main.py` 里的 `system` message，再运行一次。

观察模型回答发生了什么变化。

## 用你自己的话回答

1. `system` message 和 `user` message 有什么区别？
2. 为什么 `.env` 不应该上传到 GitHub？
3. 哪一行代码真正向模型发送了请求？
4. 哪一行代码取出了模型的回答？
5. 如果你想让 AI 像一个严格的代码审查员一样回答，你会改哪里？

# Day 13：RESTful API + FastAPI 入门

今天开始第二阶段：把 AI Demo 升级成后端 API 服务。

第一阶段主要是：

```text
Streamlit 页面 -> 调用 main.py -> 显示结果
```

第二阶段要学习：

```text
前端 / 用户 / 其他程序 -> FastAPI 接口 -> 调用 main.py -> 返回 JSON
```

## 1. API 是什么

API 可以理解成：

```text
一个程序提供给另一个程序调用的入口

API = 两个人 / 两个程序之间约定的说话方式。

在你现在的项目里：

你写了一个 RAG 检索函数
别人（前端、手机、另一个服务）想调用它
他们不能直接 import 你的 Python 函数
所以你需要在服务器上开一个 网络入口
这个入口就叫 API
```

网页、移动端、脚本、其他服务，都可以通过 API 调用后端能力。

## 2. RESTful API 先理解什么

先不用纠结复杂定义，入门阶段重点理解：

```text
GET：获取数据
POST：提交数据
JSON：前后端传数据的常见格式
状态码：告诉调用方请求是否成功
```

常见状态码：

```text
200：成功
400：请求参数有问题
404：接口或资源不存在
500：服务器内部错误
```

## 3. FastAPI 是什么

FastAPI 是 Python 里常用的后端 API 框架。

它适合 AI 应用开发，因为我们可以很方便地写：

```text
POST /chat
POST /summarize
POST /documents
POST /ask-doc
```

## 4. 今天新增了什么

新增文件：

```text
api.py
```

新增接口：

```text
GET /health
POST /echo
```

## 5. GET /health 做什么

`/health` 是健康检查接口。

它不需要传参数，只返回：

```json
{
  "status": "ok",
  "service": "ai-chat-starter-api"
}
```

它的作用是确认：

```text
FastAPI 服务已经启动成功
```

## 6. POST /echo 做什么

`/echo` 是回声接口。

请求体是：

```json
{
  "message": "你好"
}
```

响应体是：

```json
{
  "message": "你好",
  "length": 2
}
```

这个接口没有 AI 能力，只是用来理解：

```text
前端如何传 JSON 给后端
后端如何返回 JSON
```
```text
前端：
  发一个 JSON
  {"message": "你好"}

↓ FastAPI 自动转成对象

你的 Python 代码：
  request.message  →  "你好"

你返回：
  EchoResponse(message="你好", length=2)

↓ FastAPI 自动转成 JSON

前端收到：
  {"message": "你好", "length": 2}
```
## 7. Pydantic BaseModel 是什么

在 `api.py` 里：

```python
class EchoRequest(BaseModel):
    message: str
```

它规定了请求体必须包含：

```text
message 字段
并且 message 必须是字符串
```

如果调用方传错，FastAPI 会自动返回参数错误。

## 8. 今天怎么运行

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

启动 API 服务：

```powershell
python -m uvicorn api:app --reload
```

打开浏览器：

```text
http://127.0.0.1:8000/docs
```

你会看到 FastAPI 自动生成的接口测试页面。

## 9. 今天你要能讲清楚

1. FastAPI 和 Streamlit 有什么区别？
2. GET 和 POST 的区别是什么？
3. JSON 请求体是什么？
4. `/health` 为什么不需要请求体？
5. `/echo` 为什么需要请求体？
6. `BaseModel` 在接口里起什么作用？


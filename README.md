# AI Agent - 智能助手

一个前后端分离的对话式 AI Agent，支持工具调用和上下文记忆。

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 后端 | Python 3.10+ / Flask | 提供 REST API |
| 前端 | Vue 3 / Vite / Axios | 单页应用 |
| AI | OpenAI 兼容 API | 支持任意兼容接口（如小米 MiMo） |

## 名词解释

**前端相关：**
- **Node.js**：JavaScript 的运行环境，前端开发必须装。装完后自带 `npm` 命令
- **npm**：Node.js 的包管理工具，类似 Python 的 `pip`，用来安装前端库
- **package.json**：前端项目的依赖清单（类似 Python 的 `requirements.txt`），`npm install` 会根据它安装所有前端库
- **node_modules/**：`npm install` 自动生成的文件夹，存放下载的前端库（很大，不要手动改）
- **Vue**：前端框架，用来写网页界面。`.vue` 文件 = 一个界面组件（HTML + JS + CSS）
- **Vite**：前端开发工具，负责启动开发服务器、热更新、打包代码。类似 Python 的 `flask run`，但是前端版
- **Axios**：前端发 HTTP 请求的库，类似 Python 的 `requests`，用来调用后端 API
- **vite.config.js**：Vite 的配置文件，里面配了端口号、API 代理等

**后端相关：**
- **Flask**：Python 的 Web 框架，用来搭建后端 API 服务
- **pip**：Python 的包管理工具，用来安装 Python 库（类似应用商店）
- **requirements.txt**：Python 项目的依赖清单，`pip install -r requirements.txt` 会一次性安装所有需要的库

**通用概念：**
- **API**：后端提供的接口，前端通过 HTTP 请求调用，拿到 JSON 数据
- **JSON**：一种数据格式，前后端之间传数据用的，长得像 `{"name": "张三", "age": 18}`
- **localhost**：本机地址，`localhost:5000` 就是你自己电脑上的 5000 端口
- **Agent**：能自主使用工具完成任务的 AI 程序。普通 AI 只能聊天，Agent 能搜索、计算、调接口等

## 功能

- 多轮对话 + 上下文记忆
- 思考过程展示（可折叠）
- 工具调用：网页搜索（Bing）、数学计算
- 多模型切换
- 对话历史管理（保存/加载/删除）
- 加载动画（"思考中..." 闪烁点点）
- 日志记录

## 快速开始

### 1. 安装依赖

```bash
# 后端
cd ai-agent
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置 API

复制配置模板并填入你的 API 信息：

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml`：

```yaml
api:
  base_url: "https://your-api-endpoint.com/v1"
  api_key: "your-api-key"

models:
  - name: "model-id"
    label: "显示名称"

default_model: "model-id"
```

### 3. 启动

需要开两个终端：

```bash
# 终端 1：后端（端口 5000）
cd ai-agent
python app.py

# 终端 2：前端（端口 5173）
cd ai-agent/frontend
npm run dev
```

浏览器打开 `http://localhost:5173`。

## 项目结构

```
ai-agent/
├── agent/                  # Agent 核心
│   └── core.py             # LLM 调用 + 工具执行循环
├── tools/                  # 工具定义
│   ├── base.py             # 工具基类（ABC 抽象类）
│   ├── calculator.py       # 计算器（eval 安全沙箱）
│   └── web_search.py       # Bing 搜索 + HTML 解析
├── utils/                  # 工具函数
│   ├── config.py           # 读取 config.yaml
│   ├── conversation.py     # 对话持久化（JSON 文件）
│   └── logger.py           # 日志（文件 + 控制台）
├── frontend/               # Vue 前端
│   ├── src/
│   │   ├── main.js         # Vue 入口
│   │   ├── App.vue         # 主界面（状态管理 + 业务逻辑）
│   │   ├── api.js          # 后端 API 调用（axios）
│   │   └── components/
│   │       ├── Sidebar.vue         # 侧边栏（对话列表 + 模型选择）
│   │       ├── ChatWindow.vue      # 聊天区（消息列表 + 输入框 + 加载动画）
│   │       └── MessageBubble.vue   # 消息气泡（含思考过程折叠）
│   ├── package.json        # 前端依赖
│   └── vite.config.js      # Vite 配置（端口 + API 代理）
├── conversations/          # 对话记录（JSON，自动生成）
├── logs/                   # 日志文件（自动生成）
├── app.py                  # Flask API 入口
├── main.py                 # 命令行入口（备选）
├── config.yaml             # 配置文件（不提交 git）
├── config.yaml.example     # 配置模板
└── requirements.txt        # Python 依赖
```

## 架构与数据流

```
浏览器                          Flask 后端
┌──────────────────────┐      ┌──────────────────────┐
│  App.vue             │      │  app.py              │
│  ├─ Sidebar.vue      │ HTTP │  ├─ /api/chat         │──→ Agent.chat()
│  ├─ ChatWindow.vue   │◄────►│  ├─ /api/models       │
│  └─ api.js           │      │  └─ /api/conversations │
└──────────────────────┘      └──────────────────────┘
                                      │
                                      ▼
                              ┌──────────────────────┐
                              │  agent/core.py       │
                              │  ├─ 调用 LLM API     │
                              │  ├─ 解析 tool_calls  │
                              │  └─ 执行工具 → 返回  │
                              └──────────────────────┘
```

### 发消息流程

```
1. 用户输入 → App.vue.handleSend()
2. 调用 api.js.sendMessage() → POST /api/chat
3. Flask 接收 → 创建 Agent → 恢复对话历史 → 调用 agent.chat()
4. Agent 循环：调用 LLM → 判断是否有 tool_calls → 执行工具 → 再调用 LLM
5. 返回 {"thinking": "...", "content": "..."}
6. 前端显示消息 + 自动保存对话
```

### Agent 核心循环（agent/core.py）

**什么是 Agent 循环？**

普通 AI 对话：用户问 → AI 答，一轮结束。

Agent 能用工具，所以可能需要多轮。**每轮都会调一次 LLM API**：

```
用户：贵阳今天天气怎么样

第 1 次调 API：LLM 思考 → 需要查天气 → 返回 tool_calls: [web_search("贵阳天气")]
  ↓
执行工具：web_search → 返回 "贵阳，晴，25°C"
  ↓
第 2 次调 API：LLM 拿到搜索结果 → 整理成回复 → 返回 content: "贵阳今天晴天..."
  ↓
结束，返回给用户（共调了 2 次 API）
```

如果 LLM 不需要工具（比如简单聊天），第 1 次就直接返回回复，只调 1 次。最多调 max_turns=10 次。

**流程图：**

```
用户输入 → 追加到 messages → 调用 LLM API（第 N 次）
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              无 tool_calls                   有 tool_calls
                    │                               │
                    ▼                               ▼
              直接返回回复                    执行工具
                                              把工具结果追加到 messages
                                              回到顶部，再调一次 LLM
                                              （最多循环 max_turns=10 次）
```

**什么是"记忆"？**

LLM 本身没有记忆，每次调用都是独立的。我们的做法是：**每次发消息时，把整个对话历史一起发给 LLM**。

前端每次发消息，把整个对话数组传过来。后端这样处理：

```python
# app.py 第 46-49 行
agent.messages = [
    {"role": "system", "content": "你是助手..."}   # 系统提示（固定）
]
for msg in messages:                                 # 把历史全加进去
    agent.messages.append(msg)
```

最终发给 LLM 的 messages 长这样：
```
[system: 你是助手...]
[user: 你好]
[assistant: 你好！有什么可以帮你？]
[user: 1+1等于几]        ← 这次的新消息
```

LLM 看到前面的对话，就"记住"了上下文。**技术上不难，就是多传几个元素**。

**为什么有些 AI 没记忆？** 不是技术难，是成本选择。带历史 → 每次发给 LLM 的内容越来越长 → token 越多 → 越贵。很多简单应用（客服机器人、一次性问答）不需要记忆，就不传历史省钱。

- `self.messages`：对话历史列表，每次调 API 都带上
- `max_turns`：最大循环次数（默认 10），防止死循环
- 返回格式：`{"thinking": "推理过程", "content": "最终回复"}`

## API 接口

| 接口 | 方法 | 作用 |
|------|------|------|
| `/api/chat` | POST | 发消息，返回 AI 回复 |
| `/api/models` | GET | 获取可用模型列表 |
| `/api/conversations` | GET | 获取所有对话列表 |
| `/api/conversations` | POST | 保存对话 |
| `/api/conversations/<id>` | GET | 加载某个对话 |
| `/api/conversations/<id>` | DELETE | 删除对话 |

### POST /api/chat

```json
// 请求
{
  "message": "今天天气怎么样",
  "messages": [{"role": "user", "content": "..."}],
  "model": "mimo-v2.5"
}

// 响应
{
  "thinking": "用户问天气，我需要...",
  "content": "今天天气晴朗..."
}
```

## 工具系统

### 工具基类（tools/base.py）

所有工具继承 `BaseTool`，需要实现 4 个属性/方法：

```python
class MyTool(BaseTool):
    name = "tool_name"           # 工具名，LLM 通过这个名字调用
    description = "工具描述"      # 告诉 LLM 这个工具能干什么
    parameters = { ... }         # 参数定义（JSON Schema 格式）

    def execute(self, **kwargs) -> str:
        return "结果字符串"
```

`schema` 属性会自动生成 OpenAI function calling 格式的 JSON Schema。

### 添加新工具

1. 在 `tools/` 下新建文件，继承 `BaseTool`
2. 在 `app.py` 的 `create_agent()` 里注册：`agent.register_tool(MyTool())`
3. 更新 `config.yaml` 的 `system_prompt`，告诉 AI 它有这个新工具

### 内置工具

| 工具 | 说明 |
|------|------|
| `calculator` | 数学表达式计算（字符白名单 + eval） |
| `web_search` | Bing 搜索，正则解析 HTML 提取标题 |

## 配置说明（config.yaml）

```yaml
api:
  base_url: "https://api.example.com/v1"   # OpenAI 兼容接口
  api_key: "sk-..."                         # API 密钥

models:                                     # 可选模型列表
  - name: "model-id"                        # API 用的模型 ID
    label: "显示名称"                        # 前端显示的名称

default_model: "model-id"                   # 默认模型

agent:
  system_prompt: |                          # AI 的角色设定
    你是一个全能型助手...
  max_turns: 10                             # 单次对话最大工具调用轮数
  temperature: 0.7                          # 生成温度
```

## 前端组件说明

| 组件 | 职责 |
|------|------|
| `App.vue` | 全局状态管理：对话列表、当前消息、模型选择；处理发送/保存/删除逻辑 |
| `Sidebar.vue` | 左侧栏：对话列表（点击切换/×删除）、模型下拉选择、新建对话按钮 |
| `ChatWindow.vue` | 右侧聊天区：消息列表、输入框、"思考中..."加载动画 |
| `MessageBubble.vue` | 单条消息：用户消息蓝色靠右，AI 回复灰色靠左；AI 消息可展开思考过程 |
| `api.js` | 封装所有后端 API 调用（axios） |

## 开发备注

- Vite 开发服务器会自动代理 `/api/*` 到 Flask（端口 5000），无需处理跨域
- 对话记录存在 `conversations/` 目录，JSON 格式，按时间戳命名
- 日志存在 `logs/` 目录，按日期分文件（`YYYY-MM-DD.log`）
- `config.yaml` 在 `.gitignore` 中，不会被提交到 git
- **超时说明**：后端 LLM 调用超时 60 秒，前端 axios 默认 30 秒。单轮对话没问题，但如果 Agent 触发多轮工具调用（最多 10 轮），总耗时可能超过 30 秒，前端会超时。目前是同步 HTTP 响应（发请求 → 等待 → 一次性返回）

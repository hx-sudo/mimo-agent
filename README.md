# AI Agent - 从零开始的智能助手

一个用 Python + Streamlit 构建的对话式 AI Agent，支持工具调用和上下文记忆。适合小白学习 Agent 开发。

## 功能

- **对话聊天**：与 AI 模型进行多轮对话，支持上下文记忆
- **思考过程展示**：展示模型的推理过程（可折叠）
- **网页搜索**：实时搜索互联网信息（使用百度）
- **数学计算**：精确计算数学表达式
- **模型选择**：支持多个模型切换
- **对话管理**：保存、加载、删除对话历史
- **日志记录**：所有操作自动记录到日志文件

## 快速开始

### 1. 安装依赖

```bash
cd ai-agent
pip install -r requirements.txt
```

### 2. 配置 API

编辑 `config.yaml`，填入你的 API 信息：

```yaml
api:
  base_url: "你的API地址"
  api_key: "你的API密钥"

models:
  - name: "模型ID"
    label: "显示名称"

default_model: "默认模型ID"
```

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器打开 `http://localhost:8501` 即可使用。

## 项目结构

```
ai-agent/
├── agent/              # Agent 核心逻辑
│   └── core.py         # 核心循环：用户输入 → 调用LLM → 执行工具 → 返回结果
├── tools/              # 工具定义
│   ├── base.py         # 工具基类，所有工具都要继承它
│   ├── calculator.py   # 计算器工具
│   └── web_search.py   # 网页搜索工具
├── utils/              # 工具函数
│   ├── config.py       # 配置文件加载
│   ├── conversation.py # 对话历史管理（保存/加载/删除）
│   └── logger.py       # 日志记录
├── conversations/      # 对话记录（JSON 文件，自动生成）
├── app.py              # Streamlit 界面（入口文件）
├── main.py             # 命令行界面（备选入口）
├── config.yaml         # 配置文件（API地址、模型列表等）
├── requirements.txt    # Python 依赖
└── logs/               # 日志文件（自动生成）
```

## 核心代码详解

### 1. Agent 核心循环 (`agent/core.py`)

这是整个项目最重要的文件。Agent 的工作流程：

```
用户输入 → 存入消息列表 → 调用LLM → 判断是否需要工具 → 执行工具 → 继续对话
```

```python
class Agent:
    def __init__(self, model: str):
        # 初始化 API 客户端
        self.client = OpenAI(
            base_url=api_config["base_url"],
            api_key=api_config["api_key"],
        )
        self.model = model
        self.messages = []  # 对话历史
        
        # 系统提示词（决定AI的性格）
        self.messages.append({
            "role": "system", 
            "content": "你是MiMo，全能型AI助手..."
        })

    def chat(self, user_input: str) -> dict:
        """核心对话循环，返回 {"thinking": 思考过程, "content": 最终回复}"""
        # 1. 把用户消息加入历史
        self.messages.append({"role": "user", "content": user_input})

        # 2. 循环调用LLM（最多10轮，防止无限循环）
        for turn in range(self.max_turns):
            # 调用API
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": self.messages,  # 带上所有历史
                    "tools": self.tool_schemas,  # 告诉LLM有哪些工具
                }
            )
            msg = resp.json()["choices"][0]["message"]

            content = msg.get("content", "") or ""
            thinking = msg.get("reasoning_content", "") or ""
            tool_calls = msg.get("tool_calls") or []

            # 3. 判断：LLM是否要调用工具？
            if not tool_calls:
                # 不需要工具，直接返回回复
                self.messages.append({"role": "assistant", "content": content})
                return {"thinking": thinking, "content": content}

            # 需要工具 → 执行工具 → 把结果喂回去 → 再问一次
            self.messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})
            for tc in tool_calls:
                result = self._execute_tool(tc)
                self.messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
            # 继续循环，LLM看到工具结果后会生成最终回复
```

**关键概念**：

- `self.messages`：对话历史列表，每次调用API都带上，这就是"记忆"的来源
- `tool_calls`：LLM返回的工具调用请求，格式是JSON
- `max_turns`：最大循环次数，防止LLM一直调工具导致死循环
- 返回格式：`{"thinking": "思考过程", "content": "最终回复"}`，思考过程来自模型的 `reasoning_content` 字段

### 2. 工具基类 (`tools/base.py`)

所有工具都要继承这个类，实现4个属性/方法：

```python
class BaseTool(ABC):
    @property
    def name(self) -> str:
        """工具名称，LLM通过这个名字调用工具"""
        pass

    @property
    def description(self) -> str:
        """工具描述，告诉LLM这个工具能干什么"""
        pass

    @property
    def parameters(self) -> dict:
        """参数定义，JSON Schema格式，告诉LLM需要传什么参数"""
        pass

    def execute(self, **kwargs) -> str:
        """执行工具，返回字符串结果"""
        pass

    @property
    def schema(self) -> dict:
        """自动生成LLM需要的工具定义格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
```

### 3. 示例：计算器工具 (`tools/calculator.py`)

```python
class Calculator(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"  # 工具名称

    @property
    def description(self) -> str:
        return "计算数学表达式，支持加减乘除"  # LLM看这个决定什么时候用

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3 * 4'"
                }
            },
            "required": ["expression"]
        }

    def execute(self, expression: str) -> str:
        # 只允许安全的字符
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "错误：包含不允许的字符"
        return str(eval(expression))  # 执行计算
```

### 4. 界面 (`app.py`)

Streamlit 的核心概念：**每次用户交互，整个脚本从头执行一遍**。

```python
import streamlit as st
from agent.core import Agent

# 页面配置
st.set_page_config(page_title="AI Agent", layout="wide")

# 侧边栏：新建对话 + 模型选择 + 对话历史
with st.sidebar:
    col_new, col_model = st.columns([1, 3])
    # 新建按钮、模型下拉框、对话历史列表（点击切换，支持删除）

# 初始化 Agent（用 session_state 保存状态，刷新页面不丢失）
if "agent" not in st.session_state:
    st.session_state.agent = Agent(model=selected_model)
    st.session_state.agent.register_tool(Calculator())
    st.session_state.agent.register_tool(WebSearch())

# 显示历史消息（带思考过程折叠）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("thinking"):
            with st.expander("🧠 思考过程", expanded=False):
                st.markdown(msg["thinking"])
        st.markdown(msg["content"])

# 用户输入
if prompt := st.chat_input("输入你的问题..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用 Agent
    with st.chat_message("assistant"):
        result = st.session_state.agent.chat(prompt)
        if result.get("thinking"):
            with st.expander("🧠 思考过程", expanded=False):
                st.markdown(result["thinking"])
        st.markdown(result["content"])

    # 自动保存对话到 conversations/ 目录
    save_conversation(conv_id, title, messages, model)
```

**关键概念**：

- `st.session_state`：Streamlit 的状态管理，刷新页面数据不会丢
- `st.chat_input`：底部输入框
- `st.chat_message`：聊天气泡组件
- `st.expander`：可折叠区域，用于展示思考过程

### 5. 配置管理 (`utils/config.py`)

```python
import yaml

def load_config() -> dict:
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_api_config() -> dict:
    config = load_config()
    return {
        "base_url": config["api"]["base_url"],
        "api_key": config["api"]["api_key"],
    }
```

### 6. 对话管理 (`utils/conversation.py`)

对话历史以 JSON 文件形式保存在 `conversations/` 目录下，文件名格式为 `YYYYMMDD_HHMMSS.json`。

```python
from utils.conversation import (
    get_all_conversations,   # 获取所有对话列表
    load_conversation,       # 加载单个对话
    save_conversation,       # 保存对话
    delete_conversation,     # 删除对话
    generate_title,          # 根据首条消息生成标题
    new_conversation_id,     # 生成新对话 ID
)

# 保存对话
save_conversation("20260615_120000", "我的问题", messages, "mimo-v2.5")

# 加载对话
data = load_conversation("20260615_120000")
# 返回 {"title": "...", "messages": [...], "model": "..."}
```

### 7. 日志记录 (`utils/logger.py`)

```python
import logging
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # 文件日志（按日期分文件）
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/{today}.log")
    
    # 控制台日志
    console_handler = logging.StreamHandler()
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
```

## 如何添加新工具

以添加"获取当前时间"工具为例：

### 1. 创建工具文件 `tools/current_time.py`

```python
from datetime import datetime
from tools.base import BaseTool

class CurrentTime(BaseTool):
    @property
    def name(self) -> str:
        return "current_time"

    @property
    def description(self) -> str:
        return "获取当前日期和时间"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

### 2. 在 `app.py` 中注册

```python
from tools.current_time import CurrentTime

# 在初始化 Agent 时注册
st.session_state.agent.register_tool(CurrentTime())
```

### 3. 更新系统提示词 (`config.yaml`)

```yaml
system_prompt: |
  你可以使用以下工具：
  - 网页搜索：查找实时信息
  - 计算器：数学计算
  - 获取时间：查看当前日期时间
```

完成！现在AI知道它有这个工具了。

## Agent 工作流程图

```
┌─────────────────────────────────────────────────────────┐
│                    用户输入 "123*456等于多少"              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  self.messages = [                                       │
│    {"role": "system", "content": "你是AI助手..."},        │
│    {"role": "user", "content": "123*456等于多少"}         │
│  ]                                                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  调用 LLM API                                            │
│  传入: messages + tools                                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  LLM 返回: tool_calls=[calculator(expression="123*456")]│
│  (LLM决定调用计算器工具)                                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  执行工具: eval("123*456") = 56088                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  把工具结果加入消息历史:                                    │
│  {"role": "tool", "content": "56088"}                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  再次调用 LLM，这次带上工具结果                             │
│  LLM 看到结果，生成最终回复: "123×456=56088"               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  返回给用户:                                              │
│  {"thinking": "思考过程...", "content": "123×456=56088"} │
│  + 自动保存对话到 conversations/ 目录                      │
└─────────────────────────────────────────────────────────┘
```

## 常见问题

### Q: 为什么搜索失败？
A: 默认使用百度搜索。如果网络受限，检查 `tools/web_search.py` 中的搜索源。

### Q: 如何添加更多模型？
A: 编辑 `config.yaml` 的 `models` 列表：
```yaml
models:
  - name: "模型ID"
    label: "显示名称"
```

### Q: 日志在哪里？
A: 在 `logs/` 目录下，按日期分文件，如 `2026-06-15.log`。

### Q: 如何修改AI的性格？
A: 编辑 `config.yaml` 中的 `system_prompt`，这是AI的"人设说明书"。

### Q: 对话记录保存在哪里？
A: 在 `conversations/` 目录下，以 JSON 格式保存，文件名为时间戳（如 `20260615_120000.json`）。可在侧边栏查看、切换和删除对话。

## 技术栈

- **Python 3.10+**
- **Streamlit** - Web UI 框架
- **OpenAI SDK** - API 调用（兼容其他 API）
- **Requests** - HTTP 请求
- **PyYAML** - 配置文件解析

## 学习路径建议

1. **先跑起来**：按快速开始步骤启动项目
2. **理解核心循环**：重点看 `agent/core.py` 的 `chat()` 方法
3. **添加一个工具**：按"如何添加新工具"章节操作
4. **修改系统提示词**：改 `config.yaml` 看AI行为变化
5. **深入学习**：研究 ReAct、Toolformer 等 Agent 论文

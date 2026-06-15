import streamlit as st
from agent.core import Agent
from tools.calculator import Calculator
from tools.web_search import WebSearch
from utils.config import get_models, get_default_model
from utils.conversation import (
    get_all_conversations, load_conversation, save_conversation,
    delete_conversation, generate_title, new_conversation_id,
)

st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="wide")


# 初始化 session state
if "conversations" not in st.session_state:
    st.session_state.conversations = get_all_conversations()

if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# 侧边栏
with st.sidebar:
    # 顶部：新建对话 + 模型选择，一行搞定
    col_new, col_model = st.columns([1, 3])
    with col_new:
        if st.button("➕", use_container_width=True, help="新建对话"):
            if st.session_state.current_conv_id and st.session_state.messages:
                title = generate_title(st.session_state.messages)
                save_conversation(
                    st.session_state.current_conv_id, title,
                    st.session_state.messages, st.session_state.get("model", ""),
                )
            new_id = new_conversation_id()
            st.session_state.current_conv_id = new_id
            st.session_state.messages = []
            st.session_state.conversations = get_all_conversations()
            st.rerun()
    with col_model:
        models = get_models()
        model_labels = [m["label"] for m in models]
        default_model = get_default_model()
        default_index = next(i for i, m in enumerate(models) if m["name"] == default_model)
        selected_label = st.selectbox("模型", model_labels, index=default_index, label_visibility="collapsed")
        selected_model = models[model_labels.index(selected_label)]["name"]

    st.divider()

    # 对话历史列表
    st.session_state.conversations = get_all_conversations()

    if not st.session_state.conversations:
        st.caption("暂无对话记录")

    for conv in st.session_state.conversations:
        is_active = conv["id"] == st.session_state.current_conv_id
        col1, col2 = st.columns([6, 1])
        with col1:
            label = f"{'▸ ' if is_active else ''}{conv['title']}"
            if st.button(label, key=f"conv_{conv['id']}", use_container_width=True):
                if st.session_state.current_conv_id and st.session_state.messages:
                    title = generate_title(st.session_state.messages)
                    save_conversation(
                        st.session_state.current_conv_id, title,
                        st.session_state.messages, st.session_state.get("model", ""),
                    )
                data = load_conversation(conv["id"])
                st.session_state.current_conv_id = conv["id"]
                st.session_state.messages = data.get("messages", [])
                st.session_state.conversations = get_all_conversations()
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv['id']}"):
                delete_conversation(conv["id"])
                if st.session_state.current_conv_id == conv["id"]:
                    st.session_state.current_conv_id = None
                    st.session_state.messages = []
                st.session_state.conversations = get_all_conversations()
                st.rerun()



# 初始化 Agent
if "agent" not in st.session_state or st.session_state.get("model") != selected_model:
    st.session_state.agent = Agent(model=selected_model)
    st.session_state.agent.register_tool(Calculator())
    st.session_state.agent.register_tool(WebSearch())
    st.session_state.model = selected_model

# 同步 agent 的消息历史
st.session_state.agent.messages = [
    m for m in st.session_state.messages
]


# 主聊天区域
conv_title = "新对话"
if st.session_state.current_conv_id:
    for c in st.session_state.conversations:
        if c["id"] == st.session_state.current_conv_id:
            conv_title = c["title"]
            break

st.header(f"💬 {conv_title}")

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # 如果有思考过程，显示可折叠的思考区域
        if msg.get("thinking"):
            with st.expander("🧠 思考过程", expanded=False):
                st.markdown(msg["thinking"])
        st.markdown(msg["content"])

# 用户输入
if prompt := st.chat_input("输入你的问题..."):
    # 首次对话时自动创建对话
    if not st.session_state.current_conv_id:
        st.session_state.current_conv_id = new_conversation_id()

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用 agent
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            st.session_state.agent.messages = list(st.session_state.messages)
            result = st.session_state.agent.chat(prompt)

        # 显示思考过程（可折叠）
        if result.get("thinking"):
            with st.expander("🧠 思考过程", expanded=False):
                st.markdown(result["thinking"])

        # 显示最终回复
        st.markdown(result["content"])

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["content"],
        "thinking": result.get("thinking", ""),
    })

    # 自动保存对话
    title = generate_title(st.session_state.messages)
    save_conversation(
        st.session_state.current_conv_id,
        title,
        st.session_state.messages,
        selected_model,
    )
    st.session_state.conversations = get_all_conversations()

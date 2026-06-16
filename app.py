import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from agent.core import Agent
from tools.calculator import Calculator
from tools.web_search import WebSearch
from utils.config import get_models, get_default_model
from utils.conversation import (
    get_all_conversations, load_conversation, save_conversation,
    delete_conversation, generate_title, new_conversation_id,
)

DIST = Path(__file__).parent / "frontend" / "dist"

app = Flask(__name__, static_folder=str(DIST / "assets"), static_url_path="/assets")
CORS(app)


@app.route("/")
def index():
    return send_from_directory(str(DIST), "index.html")


def create_agent(model=None):
    if not model:
        model = get_default_model()
    agent = Agent(model=model)
    agent.register_tool(Calculator())
    agent.register_tool(WebSearch())
    return agent


@app.route("/api/models", methods=["GET"])
def api_models():
    return jsonify({
        "models": get_models(),
        "default": get_default_model(),
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    user_input = data.get("message", "")
    messages = data.get("messages", [])
    model = data.get("model", get_default_model())

    if not user_input:
        return jsonify({"error": "message 不能为空"}), 400

    agent = create_agent(model)
    # 恢复对话历史
    agent.messages = [{"role": "system", "content": agent.messages[0]["content"]}]
    for msg in messages:
        agent.messages.append({"role": msg["role"], "content": msg["content"]})

    result = agent.chat(user_input)
    return jsonify(result)


@app.route("/api/conversations", methods=["GET"])
def api_conversations_list():
    return jsonify({"conversations": get_all_conversations()})


@app.route("/api/conversations", methods=["POST"])
def api_conversations_save():
    data = request.json
    conv_id = data.get("id") or new_conversation_id()
    title = data.get("title") or generate_title(data.get("messages", []))
    save_conversation(conv_id, title, data.get("messages", []), data.get("model", ""))
    return jsonify({"id": conv_id, "title": title})


@app.route("/api/conversations/<conv_id>", methods=["GET"])
def api_conversations_load(conv_id):
    data = load_conversation(conv_id)
    return jsonify(data)


@app.route("/api/conversations/<conv_id>", methods=["DELETE"])
def api_conversations_delete(conv_id):
    delete_conversation(conv_id)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

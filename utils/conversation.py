import json
from pathlib import Path
from datetime import datetime

CONV_DIR = Path(__file__).parent.parent / "conversations"
CONV_DIR.mkdir(exist_ok=True)


def get_all_conversations() -> list[dict]:
    """获取所有对话列表"""
    conversations = []
    for f in sorted(CONV_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            conversations.append({
                "id": f.stem,
                "title": data.get("title", "新对话"),
                "created": data.get("created", ""),
                "updated": data.get("updated", ""),
                "message_count": len(data.get("messages", [])),
            })
        except Exception:
            continue
    return conversations


def load_conversation(conv_id: str) -> dict:
    """加载一个对话"""
    f = CONV_DIR / f"{conv_id}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {"title": "新对话", "messages": [], "model": ""}


def save_conversation(conv_id: str, title: str, messages: list, model: str):
    """保存对话"""
    data = {
        "title": title,
        "messages": messages,
        "model": model,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    f = CONV_DIR / f"{conv_id}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_conversation(conv_id: str):
    """删除对话"""
    f = CONV_DIR / f"{conv_id}.json"
    if f.exists():
        f.unlink()


def generate_title(messages: list) -> str:
    """根据第一条用户消息生成对话标题"""
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:30]
            if len(msg["content"]) > 30:
                title += "..."
            return title
    return "新对话"


def new_conversation_id() -> str:
    """生成新的对话ID"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

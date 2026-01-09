import json
import os

BASE_DIR = "./src/llm/curriculum_agent/chat_history"


def _get_chat_file_path(user_id: str, topic_id: str) -> str:
    print("called get")
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{topic_id}.json")


def load_chat_history(user_id: str, topic_id: str) -> list:
    print("called load")
    chat_file = _get_chat_file_path(user_id, topic_id)

    if not os.path.exists(chat_file):
        data = []
    else:
        with open(chat_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data

def append_response_json(user_id: str, topic_id: str, new_item):
    print("called save")
    chat_file = _get_chat_file_path(user_id, topic_id)
    if not os.path.exists(chat_file):
        data = []
    else:
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    if isinstance(new_item, list):
        data.extend(new_item)
    else:
        data.append(new_item)
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

def extract(tool_results):
    result = []
    for tool in tool_results:
        result.append(tool["input"])
        result.append(tool["output"])
    return result
import json
import os

BASE_DIR = "./chat_history"


def _get_chat_file_path(user_id: str, topic_id: str) -> str:
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{topic_id}.json")


def load_chat_history(user_id: str, topic_id: str) -> list:
    chat_file = _get_chat_file_path(user_id, topic_id)

    if not os.path.exists(chat_file):
        data = []
    else:
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

    return data


def append_response_json(user_id: str, topic_id: str, new_item):
    chat_file = _get_chat_file_path(user_id, topic_id)
    data = load_chat_history(user_id, topic_id)
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

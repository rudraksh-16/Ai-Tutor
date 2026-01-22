import json
import os

BASE_DIR = "./chat_history/curriculum_agent"


def get_file_path(user_id: str, topic_id: str) -> str:
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{topic_id}.json")
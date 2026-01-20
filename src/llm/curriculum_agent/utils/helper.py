import os

BASE_DIR = "./chat_history"


def get_file_path(user_id: str, topic_id: str) -> str:
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{topic_id}.json")
<<<<<<< Updated upstream

def parse_outline(outline_text: str) -> list[str]:
    return [
        line.strip("- ").strip()
        for line in outline_text.split("\n")
        if line.strip()
    ]
=======
>>>>>>> Stashed changes

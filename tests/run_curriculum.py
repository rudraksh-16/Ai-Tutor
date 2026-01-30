from uuid import uuid4
import os

from src.llm.main import run_curriculum_agent
from src.llm.utils import load_json, append_response_json, add_message

BASE_DIR = "./chat_history/curriculum_agent"


def get_file_path(user_id: str, topic_id: str) -> str:
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{topic_id}.json")


def run_curriculum(user_id: str, topic_id: str):
    path = get_file_path(user_id, topic_id)
    chat_history = load_json(path)

    while True:
        if chat_history:
            user_input = input("\n[You]: ").strip()
            if user_input.lower() in ("bye", "good bye"):
                break

            user_msg = {"role": "user", "content": user_input}
            chat_history.append(user_msg)
            append_response_json(path, user_msg)

        final_data = None
        print("\n[Expert] ", end="", flush=True)

        for event in run_curriculum_agent(
            user_id=user_id,
            topic_id=topic_id,
            chat_history=chat_history,
        ):
            if event["type"] == "text":
                print(event["data"], end="", flush=True)

            elif event["type"] == "tool_call":
                pass

            elif event["type"] == "final":
                final_data = event["data"]

        chat_history = add_message(final_data=final_data)
        append_response_json(path, chat_history)


def main():
    USER_ID = "0249cfc3-cce2-466e-9413-dc6db145ac5c"
    # TOPIC_ID = "4e4af430-12cd-4004-a44b-2148e3a1f03a"
    TOPIC_ID = str(uuid4())

    run_curriculum(USER_ID, TOPIC_ID)


if __name__ == "__main__":
    main()

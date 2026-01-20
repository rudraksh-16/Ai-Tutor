from uuid import uuid4

from src.llm.main import run_curriculum_agent
from src.llm.curriculum_agent.utils.helper import get_file_path
from src.llm.utils import load_json, append_response_json, extract

def run_curriculum(user_id: str, topic_id: str):
    path = get_file_path(user_id, topic_id)
    chat_history = load_json(path)
    if chat_history:
        pass
    else:
        response, tool_call = run_curriculum_agent(
            user_id=user_id, topic_id=topic_id, chat_history=chat_history
        )
        assistant_msg = {"role": "assistant", "content": response}
        chat_history.append(assistant_msg)
        append_response_json(path, assistant_msg)
        append_response_json(path, extract(tool_call))
        print(f"[AI]: {response}")

    while True:
        if chat_history:
            user_input = input("\n[You]: ").strip()
            if user_input in ("bye", "good bye"):
                break
            user_msg = {"role": "user", "content": user_input}
            chat_history.append(user_msg)
            append_response_json(path, user_msg)

        response, tool_call = run_curriculum_agent(
            user_id=user_id,
            topic_id=topic_id,
            chat_history=chat_history,
        )

        append_response_json(path, extract(tool_call))

        assistant_msg = {"role": "assistant", "content": response}
        chat_history.append(assistant_msg)
        append_response_json(path, assistant_msg)

        print(f"[AI]: {response}")


def main():
    USER_ID = "c72a838f-46be-4484-bc3e-c8bb9f438c03"
    TOPIC_ID = "e1e581fb-9f0c-4317-829d-75574b6aaa99"
    # TOPIC_ID = str(uuid4())  # generate new topic_id when needed
    run_curriculum(USER_ID, TOPIC_ID)


if __name__ == "__main__":
    main()

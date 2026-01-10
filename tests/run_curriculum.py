from uuid import uuid4

from src.llm.main import run_curriculum_agent
from src.llm.utils.helper_function import load_chat_history, append_response_json, extract

def run_curriculum(user_id: str, topic_id: str):
    chat_history = load_chat_history(user_id, topic_id)
    if chat_history:
        pass
    else:
        response, tool_call = run_curriculum_agent(
            user_id=user_id,
            topic_id=topic_id,
            chat_history=chat_history
        )
        assistant_msg = {"role": "assistant", "content": response}
        chat_history.append(assistant_msg)
        append_response_json(user_id, topic_id, assistant_msg)
        append_response_json(user_id, topic_id, extract(tool_call))
        print(f"[AI]: {response}")

    while True:
        if chat_history:
            user_input = input("\n[You]: ").strip()
            if user_input in ("bye", "good bye"):
                break
            user_msg = {"role": "user", "content": user_input}
            chat_history.append(user_msg)
            append_response_json(user_id, topic_id, user_msg)

        response, tool_call = run_curriculum_agent(
            user_id=user_id,
            topic_id=topic_id,
            chat_history=chat_history,
        )

        append_response_json(user_id, topic_id, extract(tool_call))

        assistant_msg = {"role": "assistant", "content": response}
        chat_history.append(assistant_msg)
        append_response_json(user_id, topic_id, assistant_msg)

        print(f"[AI]: {response}")



def main():
    USER_ID = "0249cfc3-cce2-466e-9413-dc6db145ac5c"
    # TOPIC_ID = "c71d9d54-39e1-43eb-8331-1560920c0474"
    # TOPIC_ID = "f4fa5222-244b-41f4-ba08-79b85a9d1470"
    TOPIC_ID = "4e4af430-12cd-4004-a44b-2148e3a1f03a"
    # TOPIC_ID = str(uuid4())  # generate new topic_id when needed
    run_curriculum(USER_ID, TOPIC_ID)


if __name__ == "__main__":
    main()

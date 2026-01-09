from uuid import uuid4

from src.llm.main import run_curriculum_agent
from src.llm.utils.helper_function import load_chat_history, append_response_json, extract

def run_curriculum(user_id: str, topic_id: str):
    chat_history = load_chat_history(user_id, topic_id)

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
    TOPIC_ID = "7fd25465-488f-49ff-b009-8ea87514b3ba"
    # TOPIC_ID = str(uuid4())  # generate new topic_id when needed
    run_curriculum(USER_ID, TOPIC_ID)


if __name__ == "__main__":
    main()

from src.llm.main import run_curriculum_agent
from src.llm.curriculum_agent.prompt import SYSTEM_PROMPT
from src.llm.utils.helper_function import load_chat_history, save_response_json
from uuid import uuid4

def run_curriculum(user_id: str, topic_id: str):
    chat_history = load_chat_history(user_id, topic_id)

    if not chat_history:
        system_msg = {"role": "system", "content": SYSTEM_PROMPT}
        chat_history.append(system_msg)
        save_response_json(user_id, topic_id, system_msg)

        user_msg = {
            "role": "user",
            "content": "Hi. I want to start creating a new learning curriculum."
        }
    else:
        user_msg = {
            "role": "user",
            "content": "Hi. I already have an existing curriculum. I want to continue working with my current topic."
        }
        
    chat_history.append(user_msg)
    save_response_json(user_id, topic_id, user_msg)

    response, messages = run_curriculum_agent(
        user_id=user_id,
        topic_id=topic_id,
        chat_history=chat_history,
        user_input=user_msg["content"]
    )

    assistant_msg = {"role": "assistant", "content": response}
    messages.append(assistant_msg)
    save_response_json(user_id, topic_id, messages)

    print(f"[AI]: {response}")

    while True:
        user_input = input("\n[You]: ").strip()

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Session ended.")
            break

        user_msg = {"role": "user", "content": user_input}
        chat_history.append(user_msg)
        save_response_json(user_id, topic_id, user_msg)

        response, messages = run_curriculum_agent(
            user_id=user_id,
            topic_id=topic_id,
            chat_history=chat_history,
            user_input=user_input
        )
        save_response_json(user_id, topic_id, messages)

        assistant_msg = {"role": "assistant", "content": response}
        chat_history.append(assistant_msg)
        save_response_json(user_id, topic_id, assistant_msg)


        print(f"[AI]: {response}")



def main():
    USER_ID = "0249cfc3-cce2-466e-9413-dc6db145ac5c"
    TOPIC_ID = "4c337091-a7c5-4985-9e5c-b0f3a41c4559"
    # TOPIC_ID = str(uuid4())  # generate new topic_id when needed



    run_curriculum(USER_ID, TOPIC_ID)


if __name__ == "__main__":
    main()

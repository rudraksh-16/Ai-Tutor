from src.llm.main import run_teacher_agent
from src.llm.utils import load_json, append_response_json, add_message


def main():
    CHAPTER_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba"
    PATH = "chat_history/teacher_agent/chat_history3.json"

    while True:
        chat_history = load_json(PATH)
        if chat_history:
            print("\n")
            user_input = input("\n[Your Response]: ").strip()
            if user_input.lower() in ("bye", "good bye"):
                break
            user = {"role": "user", "content": user_input}
            append_response_json(PATH, user)
            chat_history.append(user)

        final_data = None
        print("\n[Teacher] ", end="", flush=True)
        for event in run_teacher_agent(CHAPTER_ID, chat_history):
            if event["type"] == "text":
                print(event["data"], end="", flush=True)
            elif event["type"] == "tool_call":
                pass
            elif event["type"] == "final":
                final_data = event["data"]
        chat_history = add_message( final_data=final_data)
        append_response_json(PATH, chat_history)


if __name__ == "__main__":
    main()

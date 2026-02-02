from src.llm.main import run_teacher_agent
from src.llm.utils import load_json, append_response_json, add_message
from src.llm.teacher_agent.prompt import USER_PROMPT


def main():
    CHAPTER_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba"
    PATH = "chat_history/teacher_agent/chat_history3.json"
    chat_history = load_json(PATH)
    while True:
        user_message = ""
        if chat_history:
            user_input = input("\n\n[Your Response]: ").strip()
            if user_input.lower() in ("bye", "good bye"):
                break
            user_message = user_input
        else:
            user_message = USER_PROMPT

        final_data = None
        print("\n[Teacher] ", end="", flush=True)
        try:
            for event in run_teacher_agent(
                chapter_id=CHAPTER_ID,
                chat_history=chat_history,
                user_message=user_message,
            ):
                if event["type"] == "text":
                    print(event["data"], end="", flush=True)
                elif event["type"] == "final":
                    final_data = event["data"]
            user_input = {"role": "user", "content": user_message}
            append_response_json(PATH, user_input)
            chat_history = add_message(final_data=final_data)
            append_response_json(PATH, chat_history)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()

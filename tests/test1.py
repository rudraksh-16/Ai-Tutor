from src.llm.main import run_teacher_agent_normal
from src.llm.utils import load_json, append_response_json, extract


def main():
    TOPIC_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    PATH = "chat_history/teacher_agent/chat_history2.json"
    while True:
        chat_history = load_json(PATH)
        if chat_history:
            user_input = input("\n[Your Response]: ")
            if user_input in ("bye", "good bye"):
                break
            user = {"role": "user", "content": user_input}
            append_response_json(PATH, user)
            chat_history.append(user)

        output, tool_result = run_teacher_agent_normal(TOPIC_ID, chat_history)
        print("\n[Teacher]", output)
        result = extract(tool_result)
        assistent = {"role": "assistant", "content": output}
        result.append(assistent)
        append_response_json(PATH, result)


if __name__ == "__main__":
    main()

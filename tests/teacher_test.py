from src.llm.main import run_teacher_agent
from src.llm.utils.load_file import load_json, append_response_json, extract


def main():
    TOPIC_ID = "5c5f9b4c-7b9b-4c65-8dd1-52e9580406cd"
    PATH = "src/llm/teacher_agent/chat_history/chat_history.json"
    while True:
        chat_history = load_json(PATH)
        if chat_history:
            user_input = input("\n[Your Response]: ")
            user = {"role": "user", "content": user_input}
            append_response_json(PATH, user)
            chat_history.append(user)

        output, tool_result = run_teacher_agent(TOPIC_ID, chat_history)
        print("\n[Teacher]", output)
        result = extract(tool_result)
        assistent = {"role": "assistant", "content": output}
        result.append(assistent)
        append_response_json(PATH, result)


if __name__ == "__main__":
    main()

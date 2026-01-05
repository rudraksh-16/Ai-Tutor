from src.llm.teacher.agent import Teacher
from src.llm.teacher.tools.tools import load_file, get_user_curriculum,LoadFileArgs,GetUserCurriculumArgs


def run_iteration(topic_id):
    agent = Teacher(topic_id)
    agent.add_tool(load_file,LoadFileArgs)
    agent.add_tool(get_user_curriculum,GetUserCurriculumArgs)

    while True:
        assistant_text = agent.invoke()

        print("\n[Teacher]", assistant_text)

        agent.add_message("assistant", assistant_text)
        user_input = input("\n[Your Response]: ")

        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Goodbye!")
            break

        agent.add_message("user", user_input)

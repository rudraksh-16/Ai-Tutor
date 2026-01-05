from src.llm.teacher.agent import Teacher
from src.llm.teacher.tools.tools import (
    load_chapter_content,
    get_user_curriculum,
    LoadFileArgs,
    GetUserCurriculumArgs,
)


def run_teacher_agent(topic_id):
    agent = Teacher(topic_id)
    agent.add_tool(
        load_chapter_content,
        LoadFileArgs,
        "Load chapter content by chapter sequence and topic id.",
    )
    agent.add_tool(
        get_user_curriculum, GetUserCurriculumArgs, "Get curriculum plan by topic id."
    )

    while True:
        assistant_text = agent.invoke()

        print("\n[Teacher]", assistant_text)

        agent.add_message("assistant", assistant_text)
        user_input = input("\n[Your Response]: ")

        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Goodbye!")
            break

        agent.add_message("user", user_input)

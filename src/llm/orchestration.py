from src.llm.teacher_agent.agent import TeacherAgent
from src.llm.teacher_agent.constant import Constants
from src.llm.teacher_agent.tools.get_user_curriculum import (
    get_user_curriculum,
    GetUserCurriculumArgs,
)
from src.llm.teacher_agent.tools.get_chapter_content import (
    GetChapterArgs,
    get_chapter_content,
)


def run_teacher_agent(topic_id):
    agent = TeacherAgent(
        topic_id=topic_id,
        model=Constants.MODEL_NAME,
        max_iteration=Constants.MAX_ITERATION,
        temperature=Constants.MODEL_TEMPERATURE,
    )
    agent.add_tool(
        get_chapter_content,
        GetChapterArgs,
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

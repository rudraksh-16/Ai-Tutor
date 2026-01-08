from src.llm.curriculum_agent.agent import CurriculumAgent
from src.llm.teacher_agent.agent import TeacherAgent
from src.llm.teacher_agent.constant import TeacherConstants
from src.llm.curriculum_agent.constant import CurriculumConstants
from src.llm.curriculum_agent.tools.upsert_curriculum import (
    upsert_curriculum,
    UpsertCurriculumArgs,
)
from src.llm.curriculum_agent.tools.get_curriculum import (
    get_curriculum,
    GetCurriculumArgs,
)
from src.llm.curriculum_agent.topic_exists import topic_exists
from src.llm.teacher_agent.tools.get_user_curriculum import (
    get_user_curriculum,
    GetUserCurriculumArgs,
)
from src.llm.teacher_agent.tools.get_chapter_content import (
    GetChapterArgs,
    get_chapter_content,
)
from src.llm.planner.chapter_planner import Planner
from src.llm.planner.constant import PlannerConstants


def run_curriculum_agent(user_id: str, topic_id: str):

    agent = CurriculumAgent(
        user_id=user_id,
        topic_id=topic_id,
        model=CurriculumConstants.MODEL,
        temperature=CurriculumConstants.TEMPERATURE,
        max_iteration=CurriculumConstants.MAX_ITERATION,
    )
    agent.add_tool(
        upsert_curriculum,
        UpsertCurriculumArgs,
        description="This tool is responsible for both: saving a newly generated curriculum and updating an existing curriculum -> based on the provided input.",
    )

    agent.add_tool(
        get_curriculum,
        GetCurriculumArgs,
        description="Fetches the complete curriculum for a given topic from the database.",
    )
    exists = topic_exists(topic_id)

    if exists:
        agent.add_chat(
            "user",
            "Hi. I already have an existing curriculum. I want to continue working with my current topic.",
        )

    else:
        agent.add_chat(
            "user", "Hi. I want to start creating a new learning curriculum."
        )

    ai_response = agent.invoke()
    print("\nAI:", ai_response)

    while True:
        user_input = input("\n[You]: ").strip()

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("\nAI: Goodbye!")
            break

        agent.add_chat("user", user_input)

        ai_response = agent.invoke()
        print("\nAI:", ai_response)


def run_teacher_agent(topic_id):
    agent = TeacherAgent(
        topic_id=topic_id,
        model=TeacherConstants.MODEL_NAME,
        max_iteration=TeacherConstants.MAX_ITERATION,
        temperature=TeacherConstants.MODEL_TEMPERATURE,
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


def run_planner(topic_id: str):
    plan = Planner(
        topic_id=topic_id,
        temperature=PlannerConstants.TEMPERATURE,
        model=PlannerConstants.MODEL,
        max_retries=PlannerConstants.MAX_RETRIES,
    )
    plan.invoke()

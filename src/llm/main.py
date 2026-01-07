from src.llm.curriculum_agent.agent import CurriculumAgent
from src.llm.teacher_agent.agent import TeacherAgent
from src.llm.teacher_agent.constant import TeacherConstants
from src.llm.curriculum_agent.constant import CurriculumConstants
from src.llm.curriculum_agent.tools.save_curriculum import (
    save_curriculum,
    SaveCurriculumArgs
)
from src.llm.curriculum_agent.tools.get_curriculum import (
    get_topics,
    get_curriculum,
    GetCurriculumArgs
)
from src.llm.curriculum_agent.tools.edit_curriculum import (
    edit_curriculum,
    EditCurriculumArgs
)
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




def run_curriculum_agent(user_id: int)-> str:

    agent = CurriculumAgent(
        user_id=user_id, 
        model=CurriculumConstants.MODEL, 
        temperature=CurriculumConstants.TEMPERATURE, 
        max_iteration=CurriculumConstants.MAX_ITERATION
        )
    agent.add_tool(
        save_curriculum,
        SaveCurriculumArgs,
        description="Saves a generated curriculum after user confirmation to the database.",
    )
    agent.add_tool(
        get_curriculum,
        GetCurriculumArgs,
        description="Fetches the complete curriculum for a given topic from the database.",
    )
    agent.add_tool(
        edit_curriculum,
        EditCurriculumArgs,
        description="Modifies details of a saved curriculum chapter in the database.",
    )

    print("AI Tutor started. Type 'exit' or 'quit' to stop.\n")
    available_curriculums = get_topics(user_id)
    if available_curriculums:
        agent.add_chat(
            "system", f"User has existing curriculums: {available_curriculums}"
        )

    ai_response = agent.invoke()
    print("AI:", ai_response)

    while True:
        user_input = input("\n[You]: ").strip()

        if user_input.lower() in {"exit", "quit", "bye"}:  
            print("\nAI: Goodbye!")
            break

        agent.add_chat("user", user_input)

        ai_response = agent.invoke()
        print("\nAI:", ai_response)

    return agent.current_topic_title

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


def run_planner(TOPIC_ID: str):
    plan = Planner(
        topic_id=TOPIC_ID,
        temperature=PlannerConstants.TEMPERATURE,
        model=PlannerConstants.MODEL,
    )
    plan.invoke()
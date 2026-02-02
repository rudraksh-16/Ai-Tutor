from src.llm.curriculum_agent.agent import CurriculumAgent
from src.llm.curriculum_agent.constant import CurriculumConstants
from src.llm.curriculum_agent.tools.upsert_curriculum import make_upsert_curriculum_tool
from src.llm.curriculum_agent.tools.get_curriculum import make_get_curriculum_tool
from src.llm.curriculum_agent.tools.web_search import make_web_search_tool

from src.llm.teacher_agent.agent import TeacherAgent
from src.llm.teacher_agent.constant import TeacherConstants

from src.llm.planner.chapter_planner import Planner
from src.llm.planner.constant import PlannerConstants


def run_curriculum_agent(user_id: str, topic_id: str, chat_history: list):
    agent = CurriculumAgent(
        user_id=user_id,
        topic_id=topic_id,
        model=CurriculumConstants.MODEL,
        temperature=CurriculumConstants.TEMPERATURE,
        max_iteration=CurriculumConstants.MAX_ITERATION,
    )
    agent.add_tool(make_upsert_curriculum_tool(user_id, topic_id))
    agent.add_tool(make_get_curriculum_tool(topic_id))
    agent.add_tool(make_web_search_tool())
    ai_response = agent.stream(chat_history)
    return ai_response


def run_planner(topic_id: str):
    plan = Planner(
        topic_id=topic_id,
        temperature=PlannerConstants.TEMPERATURE,
        model=PlannerConstants.MODEL,
        max_retries=PlannerConstants.MAX_RETRIES,
    )
    plan.invoke()


def run_teacher_agent(chapter_id, chat_history, user_message):
    agent = TeacherAgent(
        chapter_id=chapter_id,
        model=TeacherConstants.MODEL_NAME,
        max_iteration=TeacherConstants.MAX_ITERATION,
        temperature=TeacherConstants.MODEL_TEMPERATURE,
    )
    try:
        for event in agent.run(chat_history=chat_history, user_message=user_message):
            yield event
    except Exception as e:
        raise e

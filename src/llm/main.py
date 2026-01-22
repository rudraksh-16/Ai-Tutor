from logger import setup_logging

# from src.llm.curriculum_agent.agent import CurriculumAgent
# from src.llm.curriculum_agent.constant import CurriculumConstants
# from src.llm.curriculum_agent.tools.upsert_curriculum import make_upsert_curriculum_tool
# from src.llm.curriculum_agent.tools.get_curriculum import make_get_curriculum_tool
# from src.llm.curriculum_agent.tools.web_search import make_web_search_tool

from src.llm.teacher_agent.agent import TeacherAgent
from src.llm.teacher_agent.constant import TeacherConstants
from src.llm.teacher_agent.tools.get_outline_content import make_get_outline_content
from src.llm.teacher_agent.tools.get_user_curriculum import make_get_user_curriculum
from src.llm.teacher_agent.tools.get_chapter import make_get_chapter
from src.llm.teacher_agent.tools.update_status import make_update_status

# from src.llm.planner.agent import PlannerAgent
# from src.llm.planner.tools.web_search import make_web_search_tool
# from src.llm.planner.constant import PlannerConstants


# setup_logging()
# def run_curriculum_agent(user_id: str, topic_id: str, chat_history: list):

#     agent = CurriculumAgent(
#         user_id=user_id,
#         topic_id=topic_id,
#         model=CurriculumConstants.MODEL,
#         temperature=CurriculumConstants.TEMPERATURE,
#         max_iteration=CurriculumConstants.MAX_ITERATION,
#     )
#     agent.add_tool(make_upsert_curriculum_tool(user_id, topic_id))

#     agent.add_tool(make_get_curriculum_tool(topic_id))

#     agent.add_tool(make_web_search_tool())

#     ai_response, tool_call = agent.invoke(chat_history)

#     return ai_response, tool_call


def run_teacher_agent(chapter_id, chat_history):
    agent = TeacherAgent(
        chapter_id=chapter_id,
        model=TeacherConstants.MODEL_NAME,
        max_iteration=TeacherConstants.MAX_ITERATION,
        temperature=TeacherConstants.MODEL_TEMPERATURE,
    )
    agent.add_tool(make_get_user_curriculum(chapter_id))
    agent.add_tool(make_get_chapter(chapter_id))
    agent.add_tool(make_get_outline_content(chapter_id))
    agent.add_tool(make_update_status(chapter_id))

    result = agent.stream(chat_history)
    return result


# def run_teacher_agent_normal(chapter_id, chat_history):
#     agent = TeacherAgent(
#         chapter_id=chapter_id,
#         model=TeacherConstants.MODEL_NAME,
#         max_iteration=TeacherConstants.MAX_ITERATION,
#         temperature=TeacherConstants.MODEL_TEMPERATURE,
#     )
#     agent.add_tool(make_get_user_curriculum(chapter_id))
#     agent.add_tool(make_get_chapter(chapter_id))
#     agent.add_tool(make_get_outline_content(chapter_id))
#     agent.add_tool(make_update_status(chapter_id))

    # assistant_text, tool_calls = agent.invoke(chat_history)
    # return assistant_text, tool_calls


# def run_planner(
#     topic_title: str,
#     user_summary: str,
#     all_chapters: list,
#     current_chapter_title: str,
#     chapter_id: str,
#     outline_title,
#     sequence: int,
#     chat_history,
# ):
#     plan = PlannerAgent(
#         topic_title=topic_title,
#         user_summary=user_summary,
#         chapter_id=chapter_id,
#         all_chapters=all_chapters,
#         current_chapter_title=current_chapter_title,
#         outline_title=outline_title,
#         sequence=sequence,
#         temperature=PlannerConstants.TEMPERATURE,
#         model=PlannerConstants.MODEL,
#     )
#     plan.add_tool(make_web_search_tool())
#     ai_response, tool_call = plan.invoke(chat_history)
#     return ai_response, tool_call

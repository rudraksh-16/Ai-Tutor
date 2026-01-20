from src.llm.main import run_planner
from src.backend.services.topic_service import TopicService
from src.backend.services.chapter_service import ChapterService
from src.backend.services.plan_service import PlanService
from src.llm.utils import load_json, append_response_json, extract


def main():
    TOPIC_ID = "e1e581fb-9f0c-4317-829d-75574b6aaa99"
    PATH = "chat_history/planner_agent/chat_history.json"
    chat_history = load_json(PATH)

    data = TopicService.get_topic_with_chapters(TOPIC_ID)
    for ch in data["chapters"]:
        outlines = ChapterService.get_chapter_with_outlines(chapter_id=ch["chapter_id"])
        i=0
        for outline in outlines["outlines"]:
            i=i+1
            assistant_msg, tool_call = run_planner(
                topic_title = data["topic_title"],
                user_summary = data["user_summary"],
                all_chapters = data["chapters"],
                current_chapter_title = ch["chapter_title"],
                chapter_id = ch["chapter_id"],
                outline_title = outline["outline_title"],
                sequence = i,
                chat_history=chat_history,
            )
            append_response_json(PATH, assistant_msg)
            append_response_json(PATH, extract(tool_call))
            PlanService.save_plan(chapter_id=ch["chapter_id"], sequence=i, plan=assistant_msg)

    

if __name__ == "__main__":
    main()

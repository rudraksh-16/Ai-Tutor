from src.backend.db.database import SessionLocal
from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan
from src.llm.teacher_agent.tools.args_schema import Args


class GetChapterArgs:
    args = [
        (
            "sequence",
            Args(type=int, description="Chapter sequence number", required=True),
        ),
        ("topic_id", Args(type=int, description="ID of the topic", required=True)),
    ]


def get_chapter_content(sequence: int, topic_id: int) -> str:
    """Load chapter content by chapter sequence and topic id."""
    db = SessionLocal()
    try:
        result = (
            db.query(ChapterPlan.content)
            .join(Chapter, Chapter.id == ChapterPlan.chapter_id)
            .filter(Chapter.topic_id == topic_id, Chapter.sequence == sequence)
            .scalar()
        )
        return result
    finally:
        db.close()

from src.backend.db.database import SessionLocal
from src.backend.models.chapter import Chapter
from src.backend.models.topic import Topic
from src.backend.models.chapter_plan import ChapterPlan
from src.llm.utils.helper import chapter_to_dict
from src.llm.teacher.tools.args_schema import Args


class LoadFileArgs:
    args = [
        (
            "sequence",
            Args(type=int, description="Chapter sequence number", required=True),
        ),
        ("topic_id", Args(type=int, description="ID of the topic", required=True)),
    ]


def load_chapter_content(sequence: int, topic_id: int) -> str:
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


class GetUserCurriculumArgs:
    args = [("topic_id", Args(type=int, description="ID of the topic", required=True))]


def get_user_curriculum(topic_id: int) -> str:
    """Get curriculum plan by topic id."""
    db = SessionLocal()
    try:
        data = (
            db.query(
                Topic.title.label("topic_title"),
                Chapter.title.label("chapter_title"),
                Chapter.sequence,
                Chapter.outline,
            )
            .join(Chapter, Chapter.topic_id == Topic.id)
            .filter(Topic.id == topic_id)
            .order_by(Chapter.sequence)
            .all()
        )
        if not data:
            raise ValueError(f"No curriculum found for topic_id={topic_id}")

        title = data[0].topic_title
        result = [chapter_to_dict(t) for t in data]
        plan = {"title": title, "curriculum": result}
        return plan
    finally:
        db.close()

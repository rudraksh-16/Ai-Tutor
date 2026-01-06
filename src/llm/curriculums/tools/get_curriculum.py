from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.curriculums.tools.argument_spec import ArgumentSpec as Args


def get_topics(user_id: int):
    db = SessionLocal()
    try:
        topics = db.query(Topic.title).filter(Topic.user_id == user_id).all()
        return topics
    finally:
        db.close()


class GetCurriculumArgs:
    args = [
        ("user_id", Args(type=int, description="The ID of the user", required=True)),
        (
            "topic_title",
            Args(type=str, description="The title of the topic", required=True),
        ),
    ]


def get_curriculum(user_id: int, topic_title: str):
    """
    Fetches the complete curriculum for a given topic from the database.
    """
    db = SessionLocal()
    try:
        topic = (
            db.query(Topic)
            .filter(Topic.user_id == user_id, Topic.title == topic_title)
            .first()
        )

        if not topic:
            return {"status": "error", "message": "Curriculum not found"}

        chapters = (
            db.query(Chapter)
            .filter(Chapter.topic_id == topic.id)
            .order_by(Chapter.sequence)
            .all()
        )

        return {
            "status": "success",
            "topic": topic.title,
            "user_summary": topic.user_summary,
            "chapters": [
                {
                    "chapter_number": c.sequence,
                    "chapter_title": c.title,
                    "chapter_outline": c.outline,
                }
                for c in chapters
            ],
        }

    finally:
        db.close()

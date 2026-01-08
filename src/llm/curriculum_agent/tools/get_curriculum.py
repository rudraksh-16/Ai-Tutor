from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal


def get_curriculum(user_id: str, topic_id: str):
    db = SessionLocal()
    topic_uuid = UUID(topic_id)
    user_uuid = UUID(user_id)
    try:
        topic = (db.query(Topic)
                 .filter(
                     Topic.id == topic_uuid,
                     Topic.user_id == user_uuid
                    )
                    .first())

        if not topic:
            return {"status": "error", "message": "Curriculum not found"}

        chapters = (
            db.query(Chapter)
            .filter(Chapter.topic_id == topic_uuid)
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

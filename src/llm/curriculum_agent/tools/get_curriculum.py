from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.curriculum_agent.tools.argument_spec import ArgumentSpec as Args


class GetCurriculumArgs:
    args = [
        (
            "topic_id",
            Args(type=str, description="The ID of the topic", required=True),
        ),
    ]


def get_curriculum(topic_id: str):
    db = SessionLocal()
    try:
        topic_uuid = UUID(topic_id)
    except ValueError:
        return {"status": "error", "message": "Invalid topic_id"}
    try:
        topic = (
            db.query(Topic)
            .filter(
                Topic.id == topic_uuid,
            )
            .first()
        )

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

    except Exception as e:
        return {"status": "error", "message": "Failed to fetch curriculum"}

    finally:
        db.close()

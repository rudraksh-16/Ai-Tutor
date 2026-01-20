from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.agent_core.tool import Tool
from sqlalchemy.orm import selectinload

def make_get_curriculum_tool(topic_id: str):
    def get_curriculum_tool():
        return get_curriculum(topic_id=topic_id)

    return Tool(
        func=get_curriculum_tool,
        description="Fetch the saved curriculum for the active topic",
    )

def get_curriculum(topic_id: str):
    db = SessionLocal()
    topic_uuid = UUID(topic_id)

    try:
        topic = db.query(Topic).filter(Topic.id == topic_uuid).first()
        if not topic:
            return {"status": "error", "message": "Topic not found"}

        chapters = (
            db.query(Chapter)
            .options(selectinload(Chapter.outlines))
            .filter(Chapter.topic_id == topic_uuid)
            .order_by(Chapter.sequence)
            .all()
        )

        return {
            "status": "success",
            "curriculum_exists": bool(chapters),
            "topic": topic.title,
            "chapters": [
                {
                    "chapter_number": c.sequence,
                    "chapter_title": c.title,
                    "chapter_outline": [
                        {
                            "outline_id": str(o.id),
                            "title": o.title,
                            "sequence": o.sequence,
                        }
                        for o in sorted(c.outlines, key=lambda x: x.sequence)
                    ],
                }
                for c in chapters
            ],
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch curriculum",
            "error_type": type(e).__name__,
        }

    finally:
        db.close()

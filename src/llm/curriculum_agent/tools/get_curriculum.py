import logging
from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.agent_core.tool import Tool

logger = logging.getLogger(__name__)


def make_get_curriculum_tool(topic_id: str):
    logger.debug(
        "Creating get curriculum tool",
        extra={"topic_id": topic_id},
    )

    def get_curriculum_tool():
        logger.info(
            "Invoking get curriculum tool",
            extra={"topic_id": topic_id},
        )
        return get_curriculum(topic_id=topic_id)

    return Tool(
        func=get_curriculum_tool,
        description="Fetch the saved curriculum for the active topic",
    )


def get_curriculum(topic_id: str):
    logger.info(
        "Starting curriculum fetch",
        extra={"topic_id": topic_id},
    )

    db = SessionLocal()
    try:
        topic_uuid = UUID(topic_id)

        logger.debug("Fetching topic from database")

        topic = (
            db.query(Topic)
            .filter(Topic.id == topic_uuid)
            .first()
        )

        if not topic:
            logger.warning(
                "Curriculum not found",
                extra={"topic_id": topic_id},
            )
            return {"status": "error", "message": "Curriculum not found"}

        logger.debug("Fetching chapters for topic")

        chapters = (
            db.query(Chapter)
            .filter(Chapter.topic_id == topic_uuid)
            .order_by(Chapter.sequence)
            .all()
        )

        logger.info(
            "Curriculum fetched successfully",
            extra={
                "topic_id": topic_id,
                "chapter_count": len(chapters),
            },
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

    except Exception:
        logger.exception(
            "Failed to fetch curriculum",
            extra={"topic_id": topic_id},
        )
        return {"status": "error", "message": "Failed to fetch curriculum"}

    finally:
        logger.debug("Closing database session")
        db.close()

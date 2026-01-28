import logging
from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from src.backend.enums.status import Status

logger = logging.getLogger(__name__)


class UpsertCurriculumArgs:
    args = [
        ("topic", Args(type=str, description="The title of topic")),
        (
            "chapter_number",
            Args(type=int, description="Chapter sequence number"),
        ),
        ("chapter_title", Args(type=str, description="Chapter title")),
        (
            "chapter_outline",
            Args(type=str, description="Detailed chapter outline"),
        ),
        (
            "user_summary",
            Args(
                type=str,
                description="Generated summary of user's learning intent",
            ),
        ),
    ]


def make_upsert_curriculum_tool(user_id: str, topic_id: str):
    logger.debug(
        "Creating upsert curriculum tool",
        extra={"user_id": user_id, "topic_id": topic_id},
    )

    def upsert_curriculum_tool(
        topic: str,
        chapter_number: int,
        chapter_title: str,
        chapter_outline: str,
        user_summary: str,
    ):
        logger.info(
            "Starting curriculum upsert",
            extra={
                "user_id": user_id,
                "topic_id": topic_id,
                "chapter_number": chapter_number,
            },
        )

        db = SessionLocal()
        try:
            user_uuid = UUID(user_id)
            topic_uuid = UUID(topic_id)

            logger.debug("Checking for existing topic")

            existing_topic = (
                db.query(Topic)
                .filter(Topic.user_id == user_uuid, Topic.id == topic_uuid)
                .first()
            )

            if existing_topic:
                logger.info(
                    "Existing topic found, updating metadata",
                    extra={"topic_id": str(existing_topic.id)},
                )
                topic_uuid = existing_topic.id
            else:
                logger.info(
                    "Creating new topic",
                    extra={"topic_id": topic_id, "title": topic},
                )
                new_topic = Topic(
                    id=topic_uuid,
                    user_id=user_uuid,
                    title=topic,
                    status=Status.PENDING.value,
                    user_summary=user_summary,
                )
                db.add(new_topic)

            logger.debug("Checking for existing chapter")

            existing_chapter = (
                db.query(Chapter)
                .filter(
                    Chapter.topic_id == topic_uuid,
                    Chapter.sequence == chapter_number,
                )
                .first()
            )

            if existing_chapter:
                logger.info(
                    "Updating existing chapter",
                    extra={
                        "chapter_sequence": chapter_number,
                        "topic_id": str(topic_uuid),
                    },
                )
                existing_chapter.title = chapter_title
                existing_chapter.outline = chapter_outline
            else:
                logger.info(
                    "Creating new chapter",
                    extra={
                        "chapter_sequence": chapter_number,
                        "topic_id": str(topic_uuid),
                    },
                )
                chapter = Chapter(
                    topic_id=topic_uuid,
                    title=chapter_title,
                    sequence=chapter_number,
                    status=Status.PENDING.value,
                    outline=chapter_outline,
                )
                db.add(chapter)

            db.commit()

            logger.info(
                "Curriculum upsert successful",
                extra={
                    "topic_id": str(topic_uuid),
                    "chapter_number": chapter_number,
                },
            )

            return {
                "status": "success",
                "message": "Curriculum saved successfully",
            }

        except Exception as e:
            logger.exception(
                "Failed to upsert curriculum",
                extra={
                    "user_id": user_id,
                    "topic_id": topic_id,
                    "chapter_number": chapter_number,
                },
            )
            db.rollback()
            return {"status": "error", "reason": str(e)}

        finally:
            logger.debug("Closing database session")
            db.close()


    return Tool(
        func=upsert_curriculum_tool,
        description="Save or update a curriculum chapter based on the provided input.",
        args_schema=UpsertCurriculumArgs,
    )

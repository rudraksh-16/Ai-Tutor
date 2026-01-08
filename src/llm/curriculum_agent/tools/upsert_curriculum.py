from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.curriculum_agent.tools.argument_spec import ArgumentSpec as Args
from src.backend.enums.status import Status


class UpsertCurriculumArgs:
    args = [
        ("user_id", Args(type=str, description="The ID of the user", required=True)),
        ("topic_id", Args(type=str, description="The ID of the topic", required=True)),
        ("topic", Args(type=str, description="The title of topic", required=True)),
        (
            "chapter_number",
            Args(type=int, description="Chapter sequence number", required=True),
        ),
        ("chapter_title", Args(type=str, description="Chapter title", required=True)),
        (
            "chapter_outline",
            Args(type=str, description="Detailed chapter outline", required=True),
        ),
        (
            "user_summary",
            Args(
                type=str,
                description="Generated summary of user's learning intent",
                required=True,
            ),
        ),
    ]


def upsert_curriculum(
    user_id: str,
    topic_id: str,
    topic: str,
    chapter_number: int,
    chapter_title: str,
    chapter_outline: str,
    user_summary: str,
) -> dict:
    """
    This tool is responsible for both:
    - saving a newly generated curriculum
    - updating an existing curriculum
    based on the provided input.
    """
    db = SessionLocal()
    user_uuid = UUID(user_id)
    topic_uuid = UUID(topic_id)
    try:
        existing_topic = (
            db.query(Topic)
            .filter(Topic.user_id == user_uuid, Topic.id == topic_uuid)
            .first()
        )
        if existing_topic:
            topic_uuid = existing_topic.id

        else:
            new_topic = Topic(
                id=topic_uuid,
                user_id=user_uuid,
                title=topic,
                status=Status.PENDING.value,
                user_summary=user_summary,
            )
            db.add(new_topic)

        existing_chapter = (
            db.query(Chapter)
            .filter(
                Chapter.topic_id == topic_uuid,
                Chapter.sequence == chapter_number,
            )
            .first()
        )

        if existing_chapter:
            existing_chapter.title = chapter_title
            existing_chapter.outline = chapter_outline

        else:
            chapter = Chapter(
                topic_id=topic_uuid,
                title=chapter_title,
                sequence=chapter_number,
                status=Status.PENDING.value,
                outline=chapter_outline,
            )

            db.add(chapter)
        db.commit()

        return {
            "status": "success",
            "message": "Curriculum saved successfully",
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "reason": str(e)}

    finally:
        db.close()

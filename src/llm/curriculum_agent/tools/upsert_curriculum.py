from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.models.outline import Outline
from src.backend.db.database import SessionLocal
from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from src.backend.enums.status import Status
from src.llm.curriculum_agent.utils.helper import parse_outline


class UpsertCurriculumArgs:
    args = [
        ("topic", Args(type=str, description="The title of topic")),
        ("chapter_number",
            Args(type=int, description="Chapter sequence number")),
        ("chapter_title", Args(type=str, description="Chapter title")),
        ("chapter_outline",
            Args(type=list, description="Detailed chapter outline")),
        ("user_summary",
            Args(
                type=str,
                description="Generated summary of user's learning intent",
            )),
    ]

def make_upsert_curriculum_tool(user_id: str, topic_id: str):
    def upsert_curriculum_tool(
        topic: str,
        chapter_number: int,
        chapter_title: str,
        chapter_outline: list[str],
        user_summary: str,
    ):
        return upsert_curriculum(
            user_id=user_id,
            topic_id=topic_id,
            topic=topic,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_outline=chapter_outline,
            user_summary=user_summary,
        )

    return Tool(

        func=upsert_curriculum_tool,
        description="Save or update a curriculum chapter",
        args_schema=UpsertCurriculumArgs
    )


def upsert_curriculum(
    user_id: str,
    topic_id: str,
    topic: str,
    chapter_number: int,
    chapter_title: str,
    chapter_outline: list[str],
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
    chapter_outline = parse_outline(chapter_outline)

    try:
        topic_obj = (
            db.query(Topic)
            .filter(Topic.id == topic_uuid)
            .first()
        )

        if not topic_obj:
            topic_obj = Topic(
                id=topic_uuid,
                user_id=user_uuid,
                title=topic,
                status=Status.PENDING.value,
                user_summary=user_summary,
            )
            db.add(topic_obj)

        chapter = (
            db.query(Chapter)
            .filter(
                Chapter.topic_id == topic_uuid,
                Chapter.sequence == chapter_number,
            )
            .first()
        )

        if chapter:
            chapter.title = chapter_title
        else:
            chapter = Chapter(
                topic_id=topic_uuid,
                title=chapter_title,
                sequence=chapter_number,
                status=Status.PENDING.value,
            )
            db.add(chapter)
            db.flush()

        db.query(Outline).filter(
            Outline.chapter_id == chapter.id
        ).delete()

        for idx, outline_text in enumerate(chapter_outline, start=1):
            db.add(
                Outline(
                    chapter_id=chapter.id,
                    sequence=idx,
                    status=Status.PENDING.value,
                    title=outline_text,
                )
            )

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

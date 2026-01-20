from uuid import UUID

from src.backend.db.database import SessionLocal
from src.backend.models.chapter import Chapter
from src.backend.models.topic import Topic
from src.backend.models.outline import Outline
from src.llm.teacher_agent.utils.helper import chapter_to_dict
from src.llm.agent_core.tool import Tool


def make_get_user_curriculum(chapter_id: str):
    def get_user_curriculum_tool():
        return get_user_curriculum(chapter_id=chapter_id)

    return Tool(
        func=get_user_curriculum_tool,
        description="Fetch the curriculum for the given chapter",
    )


def get_user_curriculum(chapter_id: str) -> dict:
    db = SessionLocal()
    try:
        chapter_uuid = UUID(chapter_id)

        # 1. Get the reference chapter (to find topic)
        ref_chapter = (
            db.query(Chapter)
            .join(Topic)
            .filter(Chapter.id == chapter_uuid)
            .one_or_none()
        )

        if not ref_chapter:
            raise ValueError("Chapter not found")

        topic = ref_chapter.topic

        # 2. Get ALL chapters of this topic
        chapters = (
            db.query(Chapter)
            .filter(Chapter.topic_id == topic.id)
            .order_by(Chapter.sequence)
            .all()
        )

        if not chapters:
            raise ValueError("No chapters found for topic")

        curriculum = []

        # 3. Attach outlines per chapter
        for chapter in chapters:
            outlines = (
                db.query(Outline)
                .filter(Outline.chapter_id == chapter.id)
                .order_by(Outline.sequence)
                .all()
            )

            curriculum.append(chapter_to_dict(chapter, outlines))

        return {
            "topic": topic.title,
            "curriculum": curriculum,
        }

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to load curriculum: {e}")

    finally:
        db.close()

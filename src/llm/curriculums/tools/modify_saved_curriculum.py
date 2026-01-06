from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.curriculums.tools.argument_spec import ArgumentSpec as Args
from typing import Optional


class modify_saved_curriculumArgs:
    args = [
        ("user_id", Args(type=int, description="The ID of the user", required=True)),
        (
            "topic_title",
            Args(type=str, description="The title of the topic", required=True),
        ),
        (
            "chapter_number",
            Args(type=int, description="Chapter sequence number", required=True),
        ),
        (
            "chapter_updated_title",
            Args(type=str, description="Updated chapter title", required=False),
        ),
        (
            "chapter_updated_outline",
            Args(
                type=str, description="Updated detailed chapter outline", required=False
            ),
        ),
    ]


def modify_saved_curriculum(
    user_id: int,
    topic_title: str,
    chapter_number: int,
    chapter_updated_title: Optional[str] = None,
    chapter_updated_outline: Optional[str] = None,
) -> dict:
    """
    Modifies details of a saved curriculum chapter in the database.

    Args:
        user_id (int): The ID of the user.
        topic_title (str): The title of the topic.
        chapter_number (int): The chapter number to be modified.
        chapter_updated_title (Optional[str]): Updated chapter title.
        chapter_updated_outline (Optional[str]): Updated chapter outline.

    Returns:
        dict: Operation result.
    """

    print(chapter_number)
    if not chapter_updated_title and not chapter_updated_outline:
        return {"status": "error", "message": "No update fields provided"}

    db = SessionLocal()
    try:
        topic_id = (
            db.query(Topic.id)
            .filter(Topic.title == topic_title, Topic.user_id == user_id)
            .limit(1)
            .scalar()
        )

        if topic_id is None:
            return {"status": "error", "message": "Topic not found."}

        chapter = (
            db.query(Chapter)
            .filter(Chapter.topic_id == topic_id, Chapter.sequence == chapter_number)
            .first()
        )

        if not chapter:
            return {"status": "error", "message": "Chapter not found."}

        if chapter_updated_title is not None:
            chapter.title = chapter_updated_title

        if chapter_updated_outline is not None:
            chapter.outline = chapter_updated_outline

        db.commit()
        db.refresh(chapter)

        return {
            "status": "success",
            "message": "Chapter updated successfully",
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "reason": str(e)}

    finally:
        db.close()

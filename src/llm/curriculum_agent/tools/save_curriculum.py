from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.db.database import SessionLocal
from src.llm.curriculum_agent.tools.argument_spec import ArgumentSpec as Args
from src.backend.enums.status import Status


class SaveCurriculumArgs:
    args = [
        ("user_id", Args(type=int, description="The ID of the user", required=True)),
        ("topic", Args(type=str, description="The curriculum topic", required=True)),
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


def save_curriculum(
    user_id: int,
    topic: str,
    chapter_number: int,
    chapter_title: str,
    chapter_outline: str,
    user_summary: str,
) -> dict:
    """
    Saves a generated curriculum after user confirmation to the database.

    Args:
        user_id (int): The ID of the user.
        topic (str): The curriculum topic.
        chapter_number (int): The chapter number.
        chapter_title (str): The chapter title.
        chapter_outline (str): The detailed chapter outline.
        user_summary (str): The generated summary of the user's learning intent.

    Returns:
        dict: A dictionary with the status of the save operation.
    """
    db = SessionLocal()
    try:
        existing_topic = (
            db.query(Topic)
            .filter(Topic.user_id == user_id, Topic.title == topic)
            .first()
        )
        if existing_topic:
            topic_id = existing_topic.id

        else:
            new_topic = Topic(
                user_id=user_id,
                title=topic,
                status=Status.PENDING.value,
                user_summary=user_summary,
            )
            db.add(new_topic)
            db.flush()
            topic_id = new_topic.id

        new_chapter = Chapter(
            topic_id=topic_id,
            title=chapter_title,
            sequence=chapter_number,
            status=Status.PENDING.value,
            outline=chapter_outline,
        )

        db.add(new_chapter)
        db.commit()

        return {
            "status": "success",
            "message": "Curriculum saved successfully",
        }

    except Exception as e:
        db.rollback()
        print(f"Database Error: {e}")
        return {"status": "error", "reason": str(e)}

    finally:
        db.close()

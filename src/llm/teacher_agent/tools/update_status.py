from src.backend.models.chapter import Chapter
from src.backend.models.outline import Outline
from src.backend.enums.status import Status
from src.backend.db.database import SessionLocal
from src.llm.agent_core.tool import Tool
from src.llm.agent_core.args_schema import ArgsSchema as Args


class UpdateOutlineStatus:
    args = [
        (
            "sequence",
            Args(type=int, description="outline sequence number", required=True),
        ),
        (
            "action",
            Args(
                type=str,
                description="Status of the outline",
                required=True,
                enum=["start", "complete"],
            ),
        ),
    ]


def make_update_status(chapter_id: str):
    def update_status_tool(sequence: int, action: str):
        return update_status(chapter_id=chapter_id, sequence=sequence, action=action)

    return Tool(
        func=update_status_tool,
        description="Update the status of the outline",
        args_schema=UpdateOutlineStatus,
    )


def update_status(chapter_id: int, sequence: int, action: str):
    db = SessionLocal()
    try:
        outline = (
            db.query(Outline)
            .filter(
                Outline.chapter_id == chapter_id,
                Outline.sequence == sequence,
            )
            .one_or_none()
        )

        if not outline:
            raise ValueError("Outline not found")

        chapter = outline.chapter
        topic = chapter.topic

        if action == "start":
            if outline.status.value == Status.PENDING.value:
                outline.status = Status.IN_PROGRESS.value

            if chapter.status.value == Status.PENDING.value:
                chapter.status = Status.IN_PROGRESS.value

            if topic.status.value == Status.PENDING.value:
                topic.status = Status.IN_PROGRESS.value
            
            

        elif action == "complete":
            outline.status = Status.COMPLETED.value

            last_outline_sequence = (
                db.query(Outline.sequence)
                .filter(Outline.chapter_id == chapter.id)
                .order_by(Outline.sequence.desc())
                .limit(1)
                .scalar()
            )

            if sequence == last_outline_sequence:
                chapter.status = Status.COMPLETED.value

                last_chapter_sequence = (
                    db.query(Chapter.sequence)
                    .filter(Chapter.topic_id == topic.id)
                    .order_by(Chapter.sequence.desc())
                    .limit(1)
                    .scalar()
                )

                if chapter.sequence == last_chapter_sequence:
                    topic.status = Status.COMPLETED.value
                
                
            
        else:
            raise ValueError("Invalid action")
        db.commit()
        return f"{action} outline {outline.title}"


    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to update status: {e}")

    finally:
        db.close()

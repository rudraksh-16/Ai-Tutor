from src.backend.db.database import SessionLocal
from src.backend.models.outline import Outline
from src.backend.models.outline_plan import OutlinePlan
from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from uuid import UUID


class GetChapterArgs:
    args = [
        (
            "sequence",
            Args(type=int, description="outline sequence number", required=True),
        )
    ]


def make_get_outline_content(chapter_id: str):
    def get_outline_content_tool(sequence: int):
        return get_outline_content(sequence=sequence, chapter_id=chapter_id)

    return Tool(
        func=get_outline_content_tool,
        description="Load outline content by outline sequence and chapter id.",
        args_schema=GetChapterArgs,
    )


def get_outline_content(sequence: int, chapter_id: str) -> str:
    """Load outline content by outline sequence and chapter id."""
    db = SessionLocal()

    try:
        chapter_id = UUID(chapter_id)
        result = (
            db.query(OutlinePlan.content)
            .join(Outline, Outline.id == OutlinePlan.outline_id)
            .filter(Outline.chapter_id == chapter_id, Outline.sequence == sequence)
            .scalar()
        )
        return result

    except Exception as e:
        raise RuntimeError(f"Failed to load the chapter {e}")

    finally:
        db.close()

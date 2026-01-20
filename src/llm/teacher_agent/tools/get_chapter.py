from src.backend.db.database import SessionLocal
from src.backend.models.chapter import Chapter
from src.backend.models.outline import Outline
from src.llm.agent_core.tool import Tool

from uuid import UUID


def make_get_chapter(chapter_id: str):
    def get_chapter_tool():
        return get_chapter(chapter_id=chapter_id)

    return Tool(
        func=get_chapter_tool,
        description="Fetch the saved curriculum for the chapter ",
    )


def get_chapter(chapter_id: str) -> dict:
    """Get chapter plan by chapter_id."""
    db = SessionLocal()
    try:
        chapter_id = UUID(chapter_id)
        data = (
            db.query(
                Chapter.title.label("chapter_title"),
                Outline.title.label("outline_title"),
                Outline.sequence,
            )
            .join(Outline, Outline.chapter_id == Chapter.id)
            .filter(Chapter.id == chapter_id)
            .order_by(Outline.sequence)
            .all()
        )
        if not data:
            raise ValueError(f"No chapter found for chapter_id={chapter_id}")

        return {
            "status": "success",
            "chapter": data[0].chapter_title,
            "outline": [
                {
                    "outline_title": outline.outline_title,
                    "sequence": outline.sequence,
                }
                for outline in data
            ],
        }

    except Exception as e:
        raise RuntimeError(f"Failed to load the chapter {e}")

    finally:
        db.close()

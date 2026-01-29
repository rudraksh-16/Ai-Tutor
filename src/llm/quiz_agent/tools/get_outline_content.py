from src.backend.db.database import SessionLocal
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.models.chapter import Chapter
from src.llm.agent_core.tool import Tool
from uuid import UUID


def make_get_outline_content(chapter_id: str, sequence: int):
    def get_outline_content_tool():
        db = SessionLocal()
        try:
            chapter_id = UUID(chapter_id)
            result = (
                db.query(ChapterPlan.content)
                .join(Chapter, Chapter.id == ChapterPlan.chapter_id)
                .filter(
                    ChapterPlan.chapter_id == chapter_id, ChapterPlan.sequence == sequence
                )
                .scalar()
            )
            return result

        except Exception as e:
            raise RuntimeError(f"Failed to load the chapter {e}")

        finally:
            db.close()

    return Tool(
        func=get_outline_content_tool,
        description="Load outline content by outline sequence and chapter id.",
    )


def get_outline_content(sequence: int, chapter_id: str) -> str:
    """Load outline content by outline sequence and chapter id."""
    
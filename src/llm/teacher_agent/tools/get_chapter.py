from src.backend.db.database import SessionLocal
from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan
from src.llm.agent_core.tool import Tool

from uuid import UUID


def make_get_chapter(chapter_id: str):
    def get_chapter_tool():
        db = SessionLocal()
        try:
            chapter_uuid = UUID(chapter_id)
            data = (
                db.query(
                    Chapter.title.label("chapter_title"),
                    ChapterPlan.title.label("outline_title"),
                    ChapterPlan.sequence,
                )
                .join(ChapterPlan, ChapterPlan.chapter_id == Chapter.id)
                .filter(Chapter.id == chapter_uuid)
                .order_by(ChapterPlan.sequence)
                .all()
            )
            if not data:
                raise ValueError(f"No chapter found for chapter_id={chapter_uuid}")

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

    return Tool(
        func=get_chapter_tool,
        description="Fetch the saved curriculum for the chapter ",
    )

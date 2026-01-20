from uuid import UUID
from sqlalchemy.orm import Session

from src.backend.db.database import SessionLocal
from src.backend.repositories.chapter_repository import ChapterQuery


class ChapterService:

    @staticmethod
    def get_chapter_with_outlines(chapter_id: str):
        if isinstance(chapter_id, UUID):
            chapter_uuid = chapter_id
        else:
            chapter_uuid = UUID(chapter_id)
        db: Session = SessionLocal()
        try:

            outlines = ChapterQuery.get_outlines_of_chapters(
                db=db,
                chapter_id=chapter_uuid
            )

            if not outlines:
                raise ValueError(f"No chapter found for chapter_id={chapter_id}")

            return {
                "chapter_title": outlines[0].chapter_title,
                "outlines": [
                    {
                        "outline_title": o.outline_title,
                        "sequence": o.sequence,
                        "status": o.Outline_status.value,
                    }
                    for o in outlines
                ]
            }

        finally:
            db.close()

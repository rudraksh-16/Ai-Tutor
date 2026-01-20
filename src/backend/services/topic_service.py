from uuid import UUID
from sqlalchemy.orm import Session

from src.backend.db.database import SessionLocal
from src.backend.repositories.topic_repository import TopicQuery


class TopicService:

    @staticmethod
    def get_topic_with_chapters(topic_id: str):
        db: Session = SessionLocal()
        try:
            topic_uuid = UUID(topic_id)

            data = TopicQuery.get_topic_chapters(
                db=db,
                topic_id=topic_uuid
            )

            if not data:
                raise ValueError(f"No chapters found for topic_id={topic_id}")

            return {
                "status": "success",
                "topic_title": data[0].topic_title,
                "user_summary": data[0].user_summary,
                "chapters": [
                    {
                        "chapter_id": row.chapter_id,
                        "chapter_title": row.chapter_title,
                        "sequence": row.sequence,
                        "status": row.chapter_status.value,
                    }
                    for row in data
                ],
            }

        finally:
            db.close()

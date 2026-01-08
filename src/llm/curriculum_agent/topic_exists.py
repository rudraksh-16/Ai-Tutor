from uuid import UUID

from src.backend.models.topic import Topic
from src.backend.db.database import SessionLocal


def topic_exists(topic_id) -> bool:
    try:
        topic_uuid = UUID(topic_id)
    except ValueError:
        return False
    db = SessionLocal()
    try:
        return (
            db.query(Topic.id)
            .filter(
                Topic.id == topic_uuid,
            )
            .first()
            is not None
        )

    finally:
        db.close()

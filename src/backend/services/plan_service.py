from uuid import UUID

from src.backend.db.database import SessionLocal
from src.backend.repositories.plan_repository import PlanQuery


class PlanService:

    @staticmethod
    def save_plan(chapter_id: str, sequence: int, plan: str):
        db = SessionLocal()
        if isinstance(chapter_id, UUID):
            chapter_uuid = chapter_id
        else:
            chapter_uuid = UUID(chapter_id)
        try:
            id = PlanQuery.get_outline_id(
                db=db,
                chapter_id=chapter_uuid,
                sequence=sequence,
            )
            return PlanQuery.save_plan(
                db=db,
                outline_id=id,
                plan=plan,
            )

        finally:
            db.close()

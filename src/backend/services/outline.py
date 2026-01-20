from src.backend.models.outline import Outline
from src.backend.models.outline_plan import OutlinePlan


class OutlineRepository:
    def load_plan(db, chapter_id, outline_sequence):
        data = (
            db.query(OutlinePlan.content)
            .join(OutlinePlan, Outline.id == OutlinePlan.outline_id)
            .filter(
                Outline.chapter_id == chapter_id, Outline.sequence == outline_sequence
            )
            .order_by(Outline.sequence)
            .scalar()
        )
        return data

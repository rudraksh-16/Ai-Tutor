from src.backend.models.outline import Outline
from src.backend.models.outline_plan import OutlinePlan


class PlanQuery:

    @staticmethod
    def get_outline_id(db, chapter_id, sequence: int):
        outline = (
            db.query(Outline.id)
            .filter(
                Outline.chapter_id == chapter_id,
                Outline.sequence == sequence,
            )
            .first()
        )

        if not outline:
            raise ValueError(
                f"No outline found for chapter_id={chapter_id}, sequence={sequence}"
            )

        return outline.id


    @staticmethod
    def save_plan(db, outline_id, plan: str):
        existing_plan = (
            db.query(OutlinePlan)
            .filter(OutlinePlan.outline_id == outline_id)
            .first()
        )

        if existing_plan:
            existing_plan.content = plan
        else:
            db.add(
                OutlinePlan(
                    outline_id=outline_id,
                    content=plan,
                )
            )

        db.commit()

        return {
            "status": "success",
            "message": "Plan saved successfully",
            "outline_id": str(outline_id),
        }

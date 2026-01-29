from uuid import UUID

from src.backend.db.database import SessionLocal
from src.backend.models.chapter import Chapter
from src.backend.models.topic import Topic
from src.llm.agent_core.tool import Tool


def make_get_user_curriculum(chapter_id: str):
    def get_user_curriculum_tool():
        db = SessionLocal()
        try:
            chapter_uuid = UUID(chapter_id)

            ref_chapter = (
                db.query(Chapter)
                .join(Topic)
                .filter(Chapter.id == chapter_uuid)
                .one_or_none()
            )

            if not ref_chapter:
                raise ValueError("Chapter not found")

            topic = ref_chapter.topic

            chapters = (
                db.query(Chapter)
                .filter(Chapter.topic_id == topic.id)
                .order_by(Chapter.sequence)
                .all()
            )

            if not chapters:
                raise ValueError("No chapters found for topic")

            return {
                "topic": topic.title,
                "user_summary": topic.user_summary,
                "chapters": [
                    {
                        "chapter_number": c.sequence,
                        "chapter_title": c.title,
                        "chapter_outline": c.outline,
                    }
                    for c in chapters
                ],
            }

        except Exception as e:
            raise RuntimeError(f"Failed to load curriculum: {e}")

        finally:
            db.close()

    return Tool(
        func=get_user_curriculum_tool,
        description="Fetch the curriculum for the given chapter",
    )



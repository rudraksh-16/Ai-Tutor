from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.models.outline import Outline


class CurriculumRepository:
    def topic_curriculum(db, topic_id):
        data = (
            db.query(
                Topic.title.label("topic_title"),
                Chapter.title.label("chapter_title"),
                Chapter.sequence.label("chapter_sequence"),
                Outline.title.label("outline_title"),
                Outline.sequence.label("outline_sequence"),
            )
            .join(Chapter, Chapter.topic_id == Topic.id)
            .join(Outline, Outline.chapter_id == Chapter.id)
            .filter(Topic.id == topic_id)
            .order_by(Chapter.sequence, Outline.sequence)
            .all()
        )
        return data

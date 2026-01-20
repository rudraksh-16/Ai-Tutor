from src.backend.models.chapter import Chapter
from src.backend.models.topic import Topic
from src.backend.models.outline import Outline

class ChapterQuery:
    def get_chapter(db, chapter_id):
        chapter = (
            db.query(Chapter)
            .filter(
                Chapter.id == chapter_id,
            )
            .first()
        )
        return chapter
    
    def insert_topic(db, topic_id, chapter_title, chapter_sequence):
        new_topic = Topic(
            id = topic_id,
            title = chapter_title,
            sequence = chapter_sequence,
        )
        db.add(new_topic)
        db.commit(new_topic)

    def get_outlines_of_chapters(db, chapter_id):
        outlines = (
            db.query(
                Chapter.title.label("chapter_title"),
                Outline.id.label("Outline_ids"),
                Outline.status.label("Outline_status"),
                Outline.title.label("outline_title"),
                Outline.sequence,
            )
            .join(Outline, Outline.chapter_id == Chapter.id)
            .filter(Chapter.id == chapter_id)
            .order_by(Outline.sequence)
            .all()
        )
        return outlines
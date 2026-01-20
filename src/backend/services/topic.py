from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter


class TopicQuery:
    def get_topic(db, topic_id):
        topic = (
            db.query(Topic)
            .filter(
                Topic.id == topic_id,
            )
            .first()
        )
        return topic

    def insert_topic(db, topic_id, user_id, topic_title, user_summary):
        new_topic = Topic(
            id=topic_id,
            user_id=user_id,
            title=topic_title,
            user_summary=user_summary,
        )
        db.add(new_topic)
        db.commit(new_topic)

    def topic_curriculum(db, topic_id):
        data = (
            db.query(
                Topic.title.label("topic_title"),
                Chapter.title.label("chapter_title"),
                Chapter.sequence,
                Chapter.outline,
            )
            .join(Chapter, Chapter.topic_id == Topic.id)
            .filter(Topic.id == topic_id)
            .order_by(Chapter.sequence)
            .all()
        )
        return data

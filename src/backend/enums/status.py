import enum


class TopicStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ChapterStatus(enum.Enum):
    LOCKED = "locked"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    QUIZ_PENDING = "quiz_pending"
    COMPLETED = "completed"

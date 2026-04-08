import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.common.exceptions import EntityNotFoundError
from src.backend.enums.status import ChapterStatus
from src.backend.models.chapter import Chapter
from src.backend.models.topic import Topic
from src.backend.repository.conversation_repo import conversation_repo
from src.backend.repository.curriculum_repo import curriculum_repo
from src.backend.repository.topic_repo import topic_repo
from src.backend.services.shared import save_stream_results, load_chat_history
from src.llm.main import run_curriculum_agent

logger = logging.getLogger(__name__)


class CurriculumService:
    """Service to handle curriculum negotiation and persistence."""

    @staticmethod
    async def get_or_create_conversation(db: AsyncSession, user_id: UUID, topic_id: UUID) -> Any:
        return await conversation_repo.get_or_create_by_topic(db, user_id, topic_id)

    @staticmethod
    async def load_chat_history(db: AsyncSession, conversation_id: UUID) -> List[Dict[str, Any]]:
        return await load_chat_history(db, conversation_id)

    @staticmethod
    async def stream_curriculum(
        user_id: UUID, topic_id: UUID, chat_history: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """Asynchronous generator that streams from the LLM agent."""
        async for event in run_curriculum_agent(str(user_id), str(topic_id), chat_history):
            yield event

    @staticmethod
    async def save_stream_results(db: AsyncSession, conversation_id: UUID, final_data: Dict[str, Any]) -> None:
        await save_stream_results(db, conversation_id, final_data)

    @classmethod
    async def upsert_curriculum_item(
        cls, 
        db: AsyncSession, 
        user_id: UUID, 
        topic_id: UUID, 
        topic_title: str,
        chapter_number: int,
        chapter_title: str,
        chapter_outline: str,
        user_summary: str
    ) -> None:
        """Delegate individual chapter upserts to the repository."""
        await curriculum_repo.upsert_curriculum_item(
            db, user_id, topic_id, topic_title, 
            chapter_number, chapter_title, chapter_outline, user_summary
        )

    @staticmethod
    async def get_curriculum_data(db: AsyncSession, topic_id: UUID) -> Dict[str, Any]:
        """Fetch the full curriculum structure for a topic."""
        return await curriculum_repo.get_curriculum_data(db, topic_id)

    @classmethod
    async def overwrite_topic_curriculum(
        cls, 
        db: AsyncSession, 
        topic_id: UUID, 
        new_title: Optional[str], 
        chapters_data: List[Any]
    ) -> None:
        """Overwrite the existing curriculum structure with new chapters.
        
        This happens when the user clicks 'Accept & Finalize' on the frontend.
        """
        topic = await topic_repo.get(db, topic_id)
        if not topic:
            raise EntityNotFoundError(f"Topic not found: {topic_id}")
        
        if new_title:
            topic.title = new_title

        # Clear existing chapters
        await db.execute(delete(Chapter).where(Chapter.topic_id == topic_id))
        
        # Create new chapters (initially LOCKED)
        for idx, chap in enumerate(chapters_data):
            # Extract items from Pydantic model or dict
            items = getattr(chap, 'items', []) if not isinstance(chap, dict) else chap.get('items', [])
            description = "\n".join(f"- {item}" for item in items)
            
            db.add(Chapter(
                topic_id=topic_id,
                title=getattr(chap, 'title') if not isinstance(chap, dict) else chap.get('title'),
                order_index=idx + 1,
                description=description,
                status=ChapterStatus.LOCKED
            ))
            
        await db.commit()

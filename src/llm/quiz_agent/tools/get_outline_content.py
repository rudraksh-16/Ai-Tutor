import logging
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import select
from src.backend.db.database import SessionLocal
from src.backend.models.chapter_plan import ChapterPlan
from src.llm.agent_core.tool import Tool

logger = logging.getLogger(__name__)


def make_get_section_content(section_id: str):
    """Factory to create a tool that fetches a single sub-chapter's content.

    Args:
        section_id: The UUID of the sub-chapter to retrieve.
    """
    async def get_section_content() -> Dict[str, Any]:
        """Fetch the title and full text content of the target sub-chapter."""
        async with SessionLocal() as db:
            res = await db.execute(
                select(ChapterPlan).filter(ChapterPlan.id == section_id)
            )
            section = res.scalars().first()
            if not section:
                return {"error": "Section not found"}
            
            return {
                "title": section.title,
                "content": section.content
            }

    return Tool(
        func=get_section_content,
        description="Fetch specific content for a sub-chapter to generate a quiz.",
    )

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.backend.common.exceptions import EntityNotFoundError
from src.backend.db.database import SessionLocal
from src.backend.enums.status import ChapterStatus
from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.models.user import User
from src.backend.repository.chapter_repo import chapter_repo
from src.backend.repository.planner_repo import planner_repo
from src.llm.planner.chapter_planner import Planner

logger = logging.getLogger(__name__)


class PlannerService:
    """Orchestrates Just-In-Time chapter plan generation (async, non-blocking)."""

    @staticmethod
    async def run_planner_and_finalize(topic_id: str) -> None:
        """Unlock the first chapter and prepare the topic for learning.
        
        This bridges the gap between curriculum negotiation and active learning.
        """
        async with SessionLocal() as db:
            # 1. Fetch Chapters for Topic
            chapters = await chapter_repo.get_by_topic(db, UUID(topic_id))
            if not chapters:
                logger.warning("No chapters found to finalize for topic %s", topic_id)
                return

            # 2. Sort and Unlock the First One
            chapters.sort(key=lambda x: x.order_index)
            first_chapter = chapters[0]
            
            if first_chapter.status == ChapterStatus.LOCKED:
                first_chapter.status = ChapterStatus.GENERATING
                await db.commit()
                logger.info("Topic %s finalized. First chapter %s background generation started.", topic_id, first_chapter.id)
                # Automatically start generating the first chapter's content
                asyncio.create_task(PlannerService._background_generate(first_chapter.id))

    @staticmethod
    async def get_or_generate_sections(
        db: AsyncSession, chapter_id: UUID, current_user: Optional[User] = None
    ) -> Optional[List[ChapterPlan]]:
        """Return existing sections, trigger async generation, or report status.

        Returns:
            List[ChapterPlan] if sections exist (READY).
            None if generation was just triggered or is in progress.
        """
        # 1. Lock the entire chapter row to prevent race conditions
        query = select(Chapter).where(Chapter.id == chapter_id).with_for_update()
        res = await db.execute(query)
        chapter = res.scalars().first()
        
        if not chapter:
            raise EntityNotFoundError(f"Chapter not found: {chapter_id}")

        # 2. Check status and existing data
        if chapter.status == ChapterStatus.GENERATING:
            return None

        if chapter.status == ChapterStatus.FAILED:
            return None

        sections = await planner_repo.get_sections(db, chapter_id)
        if sections:
            if chapter.status not in (ChapterStatus.IN_PROGRESS, ChapterStatus.COMPLETED, ChapterStatus.QUIZ_PENDING):
                chapter.status = ChapterStatus.IN_PROGRESS
                await db.commit()
            return sections

        # 3. Rate-limiting check
        if current_user:
            user_query = select(User).where(User.id == current_user.id).with_for_update()
            user_res = await db.execute(user_query)
            user = user_res.scalars().first()
            
            if user and user.last_generation_at:
                now = datetime.now(timezone.utc)
                diff = (now - user.last_generation_at).total_seconds()
                if diff < 60:
                    logger.warning("User %s rate-limited (last gen %ss ago)", user.id, int(diff))
                    raise ValueError(f"Please wait {60 - int(diff)} seconds before generating again.")
            
            if user:
                user.last_generation_at = datetime.now(timezone.utc)

        # 4. Mark as GENERATING and trigger background task
        chapter.status = ChapterStatus.GENERATING
        await db.commit()

        asyncio.create_task(PlannerService._background_generate(chapter_id))
        return None

    @staticmethod
    async def reset_chapter_for_retry(db: AsyncSession, chapter_id: UUID) -> bool:
        """Reset a chapter's status to PENDING so it can be re-generated."""
        chapter = await chapter_repo.get(db, chapter_id)
        if not chapter:
            return False
        
        chapter.status = ChapterStatus.PENDING
        await db.commit()
        logger.info("Chapter %s reset for retry.", chapter_id)
        return True

    @staticmethod
    async def recover_stuck_chapters() -> int:
        """Find chapters stuck in GENERATING for > 15 mins and mark as FAILED."""
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=15)
        
        async with SessionLocal() as db:
            query = (
                update(Chapter)
                .where(
                    and_(
                        Chapter.status == ChapterStatus.GENERATING,
                        Chapter.updated_at < timeout_threshold
                    )
                )
                .values(status=ChapterStatus.FAILED)
            )
            result = await db.execute(query)
            await db.commit()
            count = result.rowcount
            if count > 0:
                logger.warning("Recovered %d stuck chapters (marked as FAILED).", count)
            return count

    @staticmethod
    async def _background_generate(chapter_id: UUID) -> None:
        """Background task: generate sections via LLM and persist them."""
        import time
        start_time = time.time()
        try:
            async with SessionLocal() as db:
                chapter_ctx = await planner_repo.get_chapter_with_context(db, chapter_id)
                if not chapter_ctx:
                    logger.error("Chapter not found for generation: %s", chapter_id)
                    return

                planner = Planner()
                logger.info("Background generating sections for: %s", chapter_ctx.chapter_title)
                
                # LLM Call
                sections = await asyncio.wait_for(
                    planner.generate_chapter_sections(db, chapter_ctx),
                    timeout=90
                )
                
                # Implicit transaction is already open, do not use db.begin()
                query = select(Chapter).where(Chapter.id == chapter_id).with_for_update()
                res = await db.execute(query)
                chapter = res.scalars().first()
                
                if not chapter:
                    logger.error("Chapter lost during generation: %s", chapter_id)
                    return

                await planner_repo.insert_sections(db, chapter_id, sections)
                chapter.status = ChapterStatus.IN_PROGRESS
                await db.commit()

                    
                time_taken = round(time.time() - start_time, 2)
                logger.info("Background generation complete for chapter %s in %s sec", chapter_id, time_taken)

        except asyncio.TimeoutError:
            logger.error("Background generation timed out after 90 seconds for chapter %s", chapter_id)
            await PlannerService._set_chapter_failed(chapter_id)
        except IntegrityError:
            logger.warning("Duplicate generation avoided for chapter %s (IntegrityError).", chapter_id)
        except Exception as e:
            logger.exception("Background generation failed for chapter %s: %s", chapter_id, e)
            await PlannerService._set_chapter_failed(chapter_id)

    @staticmethod
    async def _set_chapter_failed(chapter_id: UUID):
        """Internal helper to mark a chapter as FAILED."""
        try:
            async with SessionLocal() as db:
                chapter = await chapter_repo.get(db, chapter_id)
                if chapter:
                    chapter.status = ChapterStatus.FAILED
                    await db.commit()
        except Exception as e:
            logger.error("Critical: Failed to set FAILED status for chapter %s: %s", chapter_id, e)

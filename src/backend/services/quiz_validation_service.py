import json
import logging
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.common.constants import PASS_THRESHOLD_PERCENT
from src.backend.common.exceptions import EntityNotFoundError
from src.backend.enums.status import ChapterStatus
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.models.quiz_attempt import QuizAttempt
from src.backend.repository.chapter_repo import chapter_repo, ChapterRepository
from src.backend.repository.quiz_attempt_repo import quiz_attempt_repo, QuizAttemptRepository
from src.backend.repository.quiz_question_repo import quiz_question_repo, QuizQuestionRepository
from src.backend.schemas.quiz import AnswerItem, QuestionFeedback, QuizResultResponse
from src.llm.quiz_agent.agent import QuizAgent

logger = logging.getLogger(__name__)


class QuizValidationService:
    """Service for score calculation, chapter progression, and quiz generation."""

    def __init__(
        self,
        question_repo: QuizQuestionRepository = quiz_question_repo,
        attempt_repo: QuizAttemptRepository = quiz_attempt_repo,
        ch_repo: ChapterRepository = chapter_repo,
    ) -> None:
        """Initialize service with injected repositories for DIP compliance."""
        self._question_repo = question_repo
        self._attempt_repo = attempt_repo
        self._chapter_repo = ch_repo

    async def generate_section_quiz(self, db: AsyncSession, section_id: UUID) -> List[Dict]:
        """Trigger the QuizAgent to generate questions for a specific section.

        Args:
            db: Database session.
            section_id: The specific sub-chapter to test.

        Returns:
            A list of generated question dictionaries.

        Raises:
            EntityNotFoundError: If the section doesn't exist.
        """
        res = await db.execute(select(ChapterPlan).filter(ChapterPlan.id == section_id))
        section = res.scalars().first()
        if not section:
            raise EntityNotFoundError(f"Section not found: {section_id}")

        agent = QuizAgent(section_id=str(section_id))
        raw_text, _ = await agent.invoke()
        
        questions = self._parse_agent_quiz_json(raw_text)
        await self.save_quiz_questions(db, section.chapter_id, questions, section_id)
        return await self.get_questions_for_user(db, section.chapter_id, section_id)

    def _parse_agent_quiz_json(self, raw_text: str) -> List[Dict]:
        """Clean and parse JSON output from the QuizAgent with robust option extraction."""
        import re
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI quiz JSON: %s. Raw: %s", e, raw_text[:200])
            raise ValueError("AI generated invalid JSON for the quiz.")

        parsed_questions = []
        for val in data.values():
            parsed_questions.append(self._extract_question_data(val))
        return parsed_questions

    def _extract_question_data(self, val: Dict) -> Dict:
        """Extract question fields robustly from a dictionary, handling various AI deviations."""
        import re
        question_text = val.get("Question") or val.get("question_text", "Untitled Question")
        options = val.get("options", [])

        # 1. Handle string-based options (e.g. "A) .. B) ..")
        if isinstance(options, str):
            options = self._split_option_string(options)

        # 2. Handle missing options field but presence of A, B, C, D keys
        if not options:
            for key in ["A", "B", "C", "D", "A)", "B)", "C)", "D)"]:
                if key in val:
                    label = key if ")" in key else f"{key})"
                    options.append(f"{label} {val[key]}")

        return {
            "question_text": question_text,
            "options": options,
            "correct_answer": val.get("correct_answer", "A").replace(")", ""),
            "explanation": val.get("explanation", "")
        }

    def _split_option_string(self, options_str: str) -> List[str]:
        """Utility to split a single string of options into a list using regex."""
        import re
        parts = re.split(r'\s*([A-D]\))\s*', options_str)
        if len(parts) > 1:
            new_options = []
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    new_options.append(f"{parts[i]} {parts[i+1]}".strip())
            return new_options
        return [options_str]

    async def save_quiz_questions(
        self, 
        db: AsyncSession, 
        chapter_id: UUID, 
        questions: List[Dict], 
        section_id: Optional[UUID] = None
    ) -> None:
        """Persist generated questions, replacing existing ones for the target."""
        if section_id:
            await self._question_repo.delete_by_section(db, section_id)
        else:
            await self._question_repo.delete_by_chapter(db, chapter_id)
            
        await self._question_repo.save_batch(db, chapter_id, questions, section_id)
        logger.info("Saved quiz questions for %s", section_id or chapter_id)

    async def get_questions_for_user(
        self, 
        db: AsyncSession, 
        chapter_id: UUID, 
        section_id: Optional[UUID] = None
    ) -> list:
        """Fetch questions for the frontend.
        
        Returns an empty list if no questions exist yet.
        """
        if section_id:
            questions = await self._question_repo.get_by_section(db, section_id)
        else:
            questions = await self._question_repo.get_by_chapter(db, chapter_id)
            
        return questions or []

    async def validate_and_record(
        self,
        db: AsyncSession,
        chapter_id: UUID,
        user_id: UUID,
        answers: List[AnswerItem],
        section_id: Optional[UUID] = None
    ) -> QuizResultResponse:
        """Score user answers and trigger progression if passed."""
        questions = await self.get_questions_for_user(db, chapter_id, section_id)
        question_map = {q.id: q for q in questions}
        
        feedback = self._build_feedback(answers, question_map)
        score = sum(1 for f in feedback if f.is_correct)
        total = len(questions)
        passed = (score / total * 100) >= PASS_THRESHOLD_PERCENT if total else False

        await self._record_attempt(db, chapter_id, user_id, score, total, passed, section_id)

        if passed:
            if section_id:
                await self._complete_section(db, section_id)
            else:
                await self.mark_chapter_completed(db, chapter_id)

        return QuizResultResponse(score=score, total=total, passed=passed, feedback=feedback)

    async def mark_chapter_completed(self, db: AsyncSession, chapter_id: UUID) -> None:
        """Public method to finalize a chapter and unlock the next one.
        
        Args:
            db: Database session.
            chapter_id: The chapter to finalize.
        """
        chapter = await self._chapter_repo.get(db, chapter_id)
        if not chapter:
            raise EntityNotFoundError(f"Chapter not found: {chapter_id}")

        chapter.status = ChapterStatus.COMPLETED
        
        # Unlock next chapter
        next_ch = await self._chapter_repo.get_next_chapter(db, chapter.topic_id, chapter.order_index)
        if next_ch:
            next_ch.status = ChapterStatus.PENDING
            
        await db.commit()
        logger.info("Chapter %s finalized and next chapter unlocked.", chapter_id)

    def _build_feedback(self, answers: List[AnswerItem], question_map: Dict) -> List[QuestionFeedback]:
        """Compare answers and build feedback response."""
        feedback = []
        for ans in answers:
            q = question_map.get(ans.question_id)
            if not q: continue
            
            feedback.append(QuestionFeedback(
                question_id=q.id,
                question_text=q.question_text,
                selected_option=ans.selected_option,
                correct_answer=q.correct_answer,
                is_correct=ans.selected_option.upper() == q.correct_answer.upper(),
                explanation=q.explanation,
            ))
        return feedback

    async def _record_attempt(
        self, db: AsyncSession, chapter_id: UUID, user_id: UUID, 
        score: int, total: int, passed: bool, section_id: Optional[UUID] = None
    ) -> None:
        """Save the quiz attempt to history."""
        db.add(QuizAttempt(
            chapter_id=chapter_id,
            section_id=section_id,
            user_id=user_id,
            score=score,
            total_questions=total,
            passed=passed,
        ))
        await db.commit()

    async def _complete_section(self, db: AsyncSession, section_id: UUID) -> None:
        """Mark a sub-chapter as complete and evaluate entire chapter status."""
        res = await db.execute(select(ChapterPlan).filter(ChapterPlan.id == section_id))
        section = res.scalars().first()
        if not section: return

        section.is_completed = True
        await db.commit()
        
        # Check overall chapter completion
        await self._check_chapter_completion(db, section.chapter_id)

    async def _check_chapter_completion(self, db: AsyncSession, chapter_id: UUID) -> None:
        """Mark chapter as completed if all its sections are done."""
        res = await db.execute(select(ChapterPlan).filter(ChapterPlan.chapter_id == chapter_id))
        all_sections = res.scalars().all()
        
        if all_sections and all(s.is_completed for s in all_sections):
            await self.mark_chapter_completed(db, chapter_id)


# Singleton instance for general use
quiz_validation_service = QuizValidationService()

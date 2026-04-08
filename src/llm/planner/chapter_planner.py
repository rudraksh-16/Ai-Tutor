import json
import logging
import re
from typing import Any, Dict, List
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db.database import SessionLocal
from src.backend.repository.planner_repo import planner_repo
from src.llm.config import LLMConfig
from src.llm.planner.constant import PlannerConstants
from src.llm.planner.prompt import SYSTEM_PROMPT, USER_PROMPT

logger = logging.getLogger(__name__)


class Planner:
    """Generates detailed teaching plans for a single curriculum chapter (JIT)."""

    def __init__(
        self,
        model: str = PlannerConstants.MODEL,
        temperature: float = PlannerConstants.TEMPERATURE,
        max_retries: int = PlannerConstants.MAX_RETRIES,
    ) -> None:
        self.client = AsyncOpenAI(api_key=LLMConfig.OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries

    async def generate_chapter_sections(
        self, db: AsyncSession, chapter_row: Any
    ) -> List[Dict[str, str]]:
        """Generate 3-4 structured sections for a single chapter.

        Args:
            db: Active database session.
            chapter_row: A row object with chapter and topic metadata.

        Returns:
            A list of section dicts with 'title' and 'content' keys.
        """
        context = self._build_context(db, chapter_row)
        raw_content = await self._generate_with_retries(chapter_row, context)
        return self._parse_sections(raw_content)

    async def _generate_with_retries(
        self, chapter_row: Any, context: Dict[str, str]
    ) -> str:
        """Call LLM with retry logic."""
        messages = self._format_prompt(chapter_row, context)

        for attempt in range(self.max_retries + 1):
            try:
                content = await self._call_llm(messages)
                logger.info("Generated plan for: %s", chapter_row.chapter_title)
                return content
            except Exception as e:
                logger.warning(
                    "Attempt %d/%d failed for %s: %s",
                    attempt + 1, self.max_retries + 1, chapter_row.chapter_title, e,
                )
                if attempt == self.max_retries:
                    raise

        raise RuntimeError("Exhausted retries without raising")

    async def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call the OpenAI chat completions API."""
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=self.temperature,
        )
        return response.choices[0].message.content or ""

    def _format_prompt(
        self, chapter_row: Any, context: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """Format system and user messages for the LLM call."""
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(
                    topic_title=chapter_row.topic_title,
                    current_chapter_title=chapter_row.chapter_title,
                    chapter_outline=chapter_row.description,
                    user_summary=context["user_summary"],
                    all_chapters=context["all_chapters_text"],
                ),
            },
        ]

    @staticmethod
    def _build_context(db: AsyncSession, chapter_row: Any) -> Dict[str, str]:
        """Extract shared context values from a chapter data row."""
        return {
            "user_summary": chapter_row.user_summary,
            "all_chapters_text": chapter_row.all_chapters_text,
        }

    @staticmethod
    def _parse_sections(raw_content: str) -> List[Dict[str, Any]]:
        """Extract and validate the JSON sections from the LLM response using Pydantic.

        Validates:
            - Valid JSON structure with 'sections' key
            - 3-4 sections present
            - Each section has 'title' and 'content' keys
            - Each section content is min 400 words
            - 'images' field is present or defaulted to []

        Raises:
            ValueError: If validation fails at any step.
        """
        from src.backend.schemas.planner_validation import ChapterSchema
        from pydantic import ValidationError

        json_text = Planner._extract_json_text(raw_content)
        
        try:
            parsed_data = json.loads(json_text)
            # Use Pydantic to validate and clean the data
            validated_chapter = ChapterSchema(**parsed_data)
            
            # Convert back to raw list of dicts for the repository
            return [s.dict() for s in validated_chapter.sections]
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM JSON: %s", e)
            raise ValueError(f"LLM returned invalid JSON: {e}") from e
        except ValidationError as e:
            logger.error("LLM JSON failed Pydantic validation: %s", e)
            raise ValueError(f"LLM content failed quality validation: {e}") from e

    @staticmethod
    def _extract_json_text(raw_content: str) -> str:
        """Extract JSON text from markdown code fences or raw content."""
        json_match = re.search(r"```json\s*(.*?)\s*```", raw_content, re.DOTALL)
        return json_match.group(1) if json_match else raw_content


from src.llm.agent_core.agent import Agent
from src.llm.planner.prompt import SYSTEM_PROMPT, USER_PROMPT
from src.llm.planner.constant import PlannerConstants

class PlannerAgent(Agent):
    def __init__(
            self,
            topic_title: str,
            user_summary: str,
            chapter_id: str,
            all_chapters: list,
            current_chapter_title: str,
            outline_title: str,
            sequence: int,
            model: str = PlannerConstants.DEFAULT_MODEL,
            temperature: float = PlannerConstants.DEFAULT_TEMPERATURE,
    ):
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT.format(
                topic_title=topic_title,
                user_summary=user_summary,
                all_chapters=all_chapters,
                current_chapter_title=current_chapter_title,
                outline_title = outline_title,
                sequence=sequence,
            ),
            model=model,
            temperature=temperature
        )
        self.chapter_id = chapter_id
        self.topic_title = topic_title
        self.user_summary = user_summary
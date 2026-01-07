from openai import OpenAI

from src.llm.planner.constant import PlannerConstants
from src.llm.config import LLMConfig
from src.llm.planner.prompt import SYSTEM_PROMPT
from src.backend.db.database import SessionLocal
from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan


class Planner:
    def __init__(
        self,
        topic_id: str,
        model: str = PlannerConstants.DEFAULT_MODEL,
        temperature: str = PlannerConstants.DEFAULT_TEMPERATURE,
    ):
        self.client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)
        self.topic_id = topic_id
        self.model = model
        self.temperature = temperature
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _call_llm(self, build_prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model, input=build_prompt, temperature=self.temperature
        )
        return response.output_text

    @staticmethod
    def build_prompt(
        topic_title: str,
        current_chapter_title: str,
        chapter_outline: str,
        user_summary: str,
        all_chapters: str,
    ):
        return f"""
            Topic:
            {topic_title}

            Learner profile:
            {user_summary}

            Full curriculum chapters (in order):
            {all_chapters}

            Current chapter:
            {current_chapter_title}

            Chapter outline:
            {chapter_outline}

            Please generate a detailed teaching plan for the current chapter.
            """

    @staticmethod
    def get_chapters(db, topic_id: str):
        return (
            db.query(
                Chapter.id.label("chapter_id"),
                Chapter.title.label("chapter_title"),
                Chapter.outline,
                Topic.title.label("topic_title"),
                Topic.user_summary.label("user_summary"),
            )
            .join(Topic, Chapter.topic_id == Topic.id)
            .filter(Topic.id == topic_id)
            .order_by(Chapter.sequence)
            .all()
        )

    @staticmethod
    def save_plan(db, id: str, plan: str):
        try:
            existing_plan = (
                db.query(ChapterPlan).filter(ChapterPlan.chapter_id == id).first()
            )
            if existing_plan:
                print(f"plan for chapter id {id} already exists")
            else:
                db.add(ChapterPlan(chapter_id=id, content=plan))
                db.commit()
            return {
                "status": "success",
                "message": "plan saved successfully",
            }
        except:
            db.rollback()
            raise

    def invoke(self):
        db = SessionLocal()
        chapters = self.get_chapters(db, self.topic_id)
        print(chapters)
        user_summary = chapters[0].user_summary
        print(user_summary)
        try:
            for ch in chapters:
                self.messages.append(
                    {
                        "role": "user",
                        "content": self.build_prompt(
                            topic_title=ch.topic_title,
                            current_chapter_title=ch.chapter_title,
                            all_chapters=chapters,
                            chapter_outline=ch.outline,
                            user_summary=user_summary,
                        ),
                    }
                )
                prompt = self.messages
                content = self._call_llm(prompt)
                self.save_plan(db, ch.chapter_id, content)
        except:
            db.rollback()
            raise
        else:
            print("Teaching content generated successfully.")
        finally:
            db.close()

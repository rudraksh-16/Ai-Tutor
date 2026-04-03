from src.llm.quiz_agent.agent import QuizAgent
from src.llm.quiz_agent.tools.get_outline_content import make_get_outline_content
from src.llm.quiz_agent.constant import QuizConstants
from src.llm.agent_core.tool import Tool


def make_create_quiz(chapter_id: str):
    async def create_quiz_tool():
        agent = QuizAgent(
            chapter_id=chapter_id,
            model=QuizConstants.MODEL,
            max_iteration=QuizConstants.MAX_ITERATION,
            temperature=QuizConstants.TEMPERATURE,
        )
        agent.add_tool(make_get_outline_content(chapter_id))

        result = await agent.invoke([])
        return result[0] if isinstance(result, tuple) else result

    return Tool(
        func=create_quiz_tool,
        description="Generate an interactive quiz covering the entire chapter content.",
    )

from src.llm.quiz_agent.agent import QuizAgent
from src.llm.quiz_agent.tools.get_outline_content import make_get_outline_content 
from src.llm.quiz_agent.constant import QuizConstants
from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool


class CreateQuizArgs:
    args = [
        (
            "sequence",
            Args(type=int, description="Outline sequence number", required=True),
        )
    ]

def make_create_quiz(chapter_id: str):
    def create_quiz_tool(sequence: int):
        agent = QuizAgent(
            chapter_id=chapter_id,
            model=QuizConstants.MODEL_NAME,
            max_iteration=QuizConstants.MAX_ITERATION,
            temperature=QuizConstants.MODEL_TEMPERATURE,
        )
        agent.add_tool(make_get_outline_content(chapter_id, sequence))

        result = agent.invoke([])
        return result
    return Tool(
        func=create_quiz_tool,
        description="Load outline content by outline sequence and chapter id.",
        args_schema=CreateQuizArgs,
    )
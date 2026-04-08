from src.llm.quiz_agent.agent import QuizAgent
from src.llm.quiz_agent.tools.get_outline_content import make_get_section_content
from src.llm.agent_core.tool import Tool


import json

def make_create_quiz(chapter_id: str):
    async def create_quiz_tool(section_id: str = None) -> str:
        """Generate an interactive mini-quiz for a specific sub-chapter.

        Args:
            section_id: The UUID of the sub-chapter to test. Defaults to chapter-level.

        Returns:
            JSON string containing section_id and the generated questions.
        """
        target_id = section_id or chapter_id
        agent = QuizAgent(section_id=target_id)
        
        raw_quiz, _ = await agent.invoke([])
        
        # Return structured data so frontend knows the context
        return json.dumps({
            "section_id": target_id,
            "quiz": raw_quiz
        })

    return Tool(
        func=create_quiz_tool,
        description="Generate an interactive quiz. Argument: section_id (sub-chapter ID).",
    )

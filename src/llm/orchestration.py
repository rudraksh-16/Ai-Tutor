from src.llm.curriculum_agent.agent import CurriculumAgent
from src.llm.curriculum_agent.tools.save_curriculum import (
    save_curriculum,
    SaveCurriculumArgs
)
from src.llm.curriculum_agent.tools.get_curriculum import (
    get_topics,
    get_curriculum,
    GetCurriculumArgs
)
from src.llm.curriculum_agent.tools.edit_curriculum import (
    edit_curriculum,
    EditCurriculumArgs
)
from src.llm.curriculum_agent.constant import Constants


def run_curriculum_agent(user_id: int):

    agent = CurriculumAgent(user_id=user_id, model=Constants.MODEL, temperature=Constants.TEMPERATURE, max_iteration=Constants.MAX_ITERATION)
    agent.add_tool(
        save_curriculum,
        SaveCurriculumArgs,
        description="Saves a generated curriculum after user confirmation to the database.",
    )
    agent.add_tool(
        get_curriculum,
        GetCurriculumArgs,
        description="Fetches the complete curriculum for a given topic from the database.",
    )
    agent.add_tool(
        edit_curriculum,
        EditCurriculumArgs,
        description="Modifies details of a saved curriculum chapter in the database.",
    )

    print("AI Tutor started. Type 'exit' or 'quit' to stop.\n")
    available_curriculums = get_topics(user_id)
    if available_curriculums:
        agent.add_chat(
            "system", f"User has existing curriculums: {available_curriculums}"
        )

    ai_response = agent.invoke()
    print("AI:", ai_response)

    while True:
        user_input = input("\n[You]: ").strip()

        if user_input.lower() in {"exit", "quit", "bye"}:  
            print("\nAI: Goodbye!")
            break

        agent.add_chat("user", user_input)

        ai_response = agent.invoke()
        print("\nAI:", ai_response)

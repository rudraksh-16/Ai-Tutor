from src.llm.curriculums.agent import CurriculumAgent
from src.llm.curriculums.tools.save_curriculum import (
    save_curriculum,
    save_curriculumArgs,
)
from src.llm.curriculums.tools.get_curriculum import (
    get_curriculum_topics,
    get_curriculum,
    get_curriculumArgs,
)
from src.llm.curriculums.tools.modify_saved_curriculum import (
    modify_saved_curriculum,
    modify_saved_curriculumArgs,
)


def run_curriculum_agent(user_id: int):

    agent = CurriculumAgent(user_id=user_id)
    agent.add_tool(
        save_curriculum,
        save_curriculumArgs,
        description="Saves a generated curriculum after user confirmation to the database.",
    )
    agent.add_tool(
        get_curriculum,
        get_curriculumArgs,
        description="Fetches the complete curriculum for a given topic from the database.",
    )
    agent.add_tool(
        modify_saved_curriculum,
        modify_saved_curriculumArgs,
        description="Modifies details of a saved curriculum chapter in the database.",
    )

    print("AI Tutor started. Type 'exit' or 'quit' to stop.\n")
    available_curriculums = get_curriculum_topics(user_id)
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

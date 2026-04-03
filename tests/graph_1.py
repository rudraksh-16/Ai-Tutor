from src.llm.graph import workflow
from src.llm.utils import load_json, append_response_json, extract
from langgraph.types import Command
import asyncio
from src.llm.graph import workflow


async def main():
    initial_state = {
        "chat_history": [],
        "chapter_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba",
        "mode": "teach",
        "waiting_for_user": False,
        "sequence": 1,
        "teaching_completed": False,
    }

    print("hi")

    async for chunk in workflow.astream(
        initial_state,
        stream_mode="custom",
    ):
        if chunk["type"] == "token":
            print(chunk["data"], end="", flush=True)

        elif chunk["type"] == "tool_call":
            pass
            # print("\n[Tool]", chunk["data"])


if __name__ == "__main__":
    asyncio.run(main())

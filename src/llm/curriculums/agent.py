import json
from openai import OpenAI

from src.llm.config import LLMConfig
from src.llm.curriculums.prompts.system_prompts import SYSTEM_PROMPT
from src.llm.curriculums.tools.tool_registry import ToolRegistry


class CurriculumAgent:
    def __init__(self, user_id: int, model: str = "gpt-4.1-mini", temperature: float = 0.2):
        self.client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)
        self.user_id = user_id
        self.model = model
        self.temperature = temperature
        self.tools = {}
        self.chat_history = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "Would you ask me about do i want to add new curriculum or view and edit already existing curriculum in one line.",
            },
        ]

        self.saved_chapters = set()
        self.save_failures = 0


        self.curriculum_saved = False

    def add_chat(self, role: str, content: str):
        self.chat_history.append({
            "role": role,
            "content": content
        })

    def add_tool(self, func, args_class, description: str = None):
        tool = ToolRegistry(func, args_class, description)
        self.tools[tool.name] = tool

    def execute_tool(self, name: str, args: dict):
        args["user_id"] = self.user_id

        if name == "save_curriculum" and self.curriculum_saved:
            return {"status": "ignored", "reason": "already_saved"}

        return self.tools[name].execute(**args)

    def _call_llm(self):
        return self.client.responses.create(
            model=self.model,
            input=self.chat_history,
            temperature=self.temperature,
            tools=[t.schema() for t in self.tools.values()],
            tool_choice="auto",
        )
    
    def invoke(self):
        max_steps = 10
        step = 0

        while step < max_steps:
            
            step += 1

            response = self._call_llm()

            assistant_text = ""
            tool_calls = []

            for item in response.output:
                if item.type == "message" and item.role == "assistant":
                    for block in item.content:
                        if block.type == "output_text":
                            assistant_text += block.text

                elif item.type in {"tool_call", "function_call"}:
                    tool_calls.append(item)

            if tool_calls:

                for call in tool_calls:
                    args = json.loads(call.arguments)

                    self.chat_history.append({
                        "type": "function_call",
                        "name": call.name,
                        "arguments": json.dumps(args),
                        "call_id": call.id,
                        })
                    
                    result = self.execute_tool(call.name, args)

                    self.chat_history.append({
                        "type": "function_call_output",
                        "call_id": call.id,
                        "output": json.dumps(result),
                    })

                    if call.name == "save_curriculum":
                        chapter_no = args.get("chapter_number")

                        if result.get("status") == "success":
                            self.saved_chapters.add(chapter_no)
                            self.save_failures = 0
                        else:
                            self.save_failures += 1

                    self.add_chat(
                        "developer",
                        json.dumps({
                            "type": "tool_result",
                            "tool_name": call.name,
                            "arguments": args,
                            "result": result,
                        }),
                    )

                if self.save_failures > 1:
                    return "Apologies, there was an issue saving your curriculum."

                continue

            if assistant_text:
                self.add_chat("assistant", assistant_text)
                return assistant_text

        return "Something went wrong. Please try again."
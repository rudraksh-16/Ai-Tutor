import json
from openai import OpenAI

from src.llm.config import LLMConfig
from src.llm.curriculum_agent.prompt import SYSTEM_PROMPT
from src.llm.curriculum_agent.tools.tool_registry import ToolRegistry
from src.llm.curriculum_agent.constant import CurriculumConstants


class CurriculumAgent:
    def __init__(
        self,
        user_id: str,
        topic_id: str = None,
        model: str = CurriculumConstants.DEFAULT_MODEL,
        temperature: float = CurriculumConstants.DEFAULT_TEMPERATURE,
        max_iteration: int = CurriculumConstants.DEFAULT_MAX_ITERATION,
    ):
        self.client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)
        self.user_id = user_id
        self.topic_id = topic_id
        self.model = model
        self.temperature = temperature
        self.tools = {}
        self.chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        self.max_iteration = max_iteration

        self.saved_chapters = set()
        self.save_failures = 0

        self.curriculum_saved = False

    def add_chat(self, role: str, content: str):
        self.chat_history.append({"role": role, "content": content})

    def add_tool(self, func, args_class, description: str = None):
        tool = ToolRegistry(func, args_class, description)
        self.tools[tool.name] = tool

    def execute_tool(self, name: str, args: dict):
        args["user_id"] = self.user_id
        args["topic_id"] = self.topic_id

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
        max_iteration = self.max_iteration
        step = 0

        while step < max_iteration:

            step += 1
            response = self._call_llm()

            assistant_text = ""
            print(response.output)
            for item in response.output:
                if item.type == "function_call":
                    tool_name = item.name
                    args = json.loads(item.arguments)

                    self.chat_history.append(
                        {
                            "type": "function_call",
                            "name": tool_name,
                            "arguments": json.dumps(args),
                            "call_id": item.id,
                        }
                    )

                    result = self.execute_tool(item.name, args)

                    self.chat_history.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.id,
                            "output": json.dumps(result),
                        }
                    )

                    if tool_name == "save_curriculum":

                        if result.get("status") == "success":
                            self.saved_chapters.add(args.get("chapter_number"))
                            self.save_failures = 0
                        else:
                            self.save_failures += 1
                elif item.type == "message":
                    for part in item.content:
                        if part.type == "output_text":
                            assistant_text += part.text

            if self.save_failures > 1:
                return "Apologies, there was an issue saving your curriculum."

            if assistant_text and step <= max_iteration:
                self.add_chat("assistant", assistant_text)
                return assistant_text

        return "Something went wrong. Please try again."

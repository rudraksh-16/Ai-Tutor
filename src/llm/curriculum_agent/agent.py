import json
from openai import OpenAI

from src.llm.config import LLMConfig
from src.llm.curriculum_agent.prompt import SYSTEM_PROMPT
from src.llm.curriculum_agent.tools.tool_registry import ToolRegistry
from src.llm.curriculum_agent.constant import Constants


class CurriculumAgent:
    def __init__(
        self,
        user_id: int,
        model: str = Constants.DEFAULT_MODEL,
        temperature: float = Constants.DEFAULT_TEMPERATURE,
        max_iteration: int = Constants.DEFAULT_MAX_ITERATION
    ):
        self.client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)
        self.user_id = user_id
        self.model = model
        self.temperature = temperature
        self.tools = {}
        self.chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "system",
                "content": "Ask the user if they would like to create a new curriculum or manage an existing one in a single sentence.",
            },
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
    
    def format_chat_history(self, input: list) -> list:
        chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Hello, I want to start a new learning journey.",
            },
        ]

        if isinstance(input, list):
            chat_history.extend(input)
        else:
            chat_history.append(input)

        return chat_history

    def invoke(self, chat_history: list):
        chat_history = self.format_chat_history(chat_history)
        step = 0
        tool_calls=[]

        while step < self.max_iteration:

            step += 1
            response = self._call_llm()

            assistant_text = ""
            # tool_calls = []
            print(response.output)
            for item in response.output:
                if item.type == "function_call":
                    tool_name = item.name
                    args = json.loads(item.arguments)

                    tool_input={
                        "type": "function_call",
                        "name": tool_name,
                        "arguments": json.dumps(args),
                        "call_id": item.call_id,
                    }
                    chat_history.append(tool_input)

                    result = self.execute_tool(item.name, args)

                    tool_output={
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                    tool_calls.append({"input": tool_input, "output": tool_output})
                    chat_history.append(tool_output)

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

            if assistant_text and step <= self.max_iteration:
                self.add_chat("assistant", assistant_text)
                return assistant_text

        return "Something went wrong. Please try again."

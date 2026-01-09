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
        topic_id: str,
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
        self.max_iteration = max_iteration

        self.saved_chapters = set()
        self.save_failures = 0

    def add_tool(self, func, args_class, description: str = None):
        tool = ToolRegistry(func, args_class, description)
        self.tools[tool.name] = tool

    def execute_tool(self, name: str, args: dict):
        tool = self.tools[name]
        arg_names = {arg_name for arg_name, _ in tool.args_schema.args}

        if "user_id" in arg_names:
            args["user_id"] = self.user_id

        if "topic_id" in arg_names:
            args["topic_id"] = self.topic_id

        return self.tools[name].execute(**args)

    def _call_llm(self, chat_history):
        return self.client.responses.create(
            model=self.model,
            input=chat_history,
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
        tool_call=[]
        step = 0
        tool_calls = []

        while step < self.max_iteration:
            step += 1
            response = self._call_llm(chat_history)
            assistant_text = ""

            for item in response.output:
                if item.type == "function_call":
                    tool_name = item.name
                    args = json.loads(item.arguments)

                    tool_input = {
                        "type": "function_call",
                        "name": tool_name,
                        "arguments": json.dumps(args),
                        "call_id": item.call_id,
                    }
                    chat_history.append(tool_input)

                    result = self.execute_tool(tool_name, args)

                    tool_output = {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                    tool_calls.append({"input": tool_input, "output": tool_output})
                    chat_history.append(tool_output)

                    if tool_name == "upsert_curriculum":
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
                return CurriculumConstants.ERROR_SAVE_CURRICULUM

            if assistant_text:
                return assistant_text, tool_calls

        return CurriculumConstants.ERROR_GENERIC, tool_calls

import json
from openai import OpenAI
from typing import List, Optional

from src.llm.config import LLMConfig
from src.llm.utils.constant import Constants
from src.llm.utils.tool import Tool


class Agent:

    def __init__(
        self,
        system_prompt: str,
        user_prompt: str = None,
        model: str = Constants.DEFAULT_MODEL,
        temperature: float = Constants.DEFAULT_TEMPERATURE,
        max_iteration: int = Constants.DEFAULT_MAX_ITERATION,
    ):
        self.client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)

        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.model = model
        self.temperature = temperature
        self.max_iteration = max_iteration
        self.tools = {}

    def add_tool(self, func, args_class=None, description=None):
        tool = Tool(func, args_class, description)
        self.tools[tool.name] = tool

    def on_tool_result(self, tool_name: str, args: dict, result: dict):
        pass

    def _execute_tool(self, name: str, args: Optional[dict]):
        if args:
            return self.tools[name].execute(**args)
        return self.tools[name].execute()

    def _call_llm(self, chat_history: List[dict]):
        return self.client.responses.create(
            model=self.model,
            temperature=self.temperature,
            input=chat_history,
            tools=[tool.schema() for tool in self.tools.values()],
            tool_choice="auto",
        )
    
    def _final_tool_args(self, tool, llm_args: dict) -> dict:
        if not tool.manual_arg:
            return llm_args

        manual_args = {}
        missing = []

        for arg in tool.manual_arg:
            if hasattr(self, arg):
                manual_args[arg] = getattr(self, arg)
            else:
                missing.append(arg)

        if missing:
            raise RuntimeError(
                f"Missing required manual args for tool '{tool.name}': {missing}"
            )

        return {**llm_args, **manual_args}
                    

    def _format_chat_history(self, user_input: list[dict]) -> List[dict]:
        history = [
            {"role": "system", "content": self.system_prompt},
        ]
        if self.user_prompt:
            history.append({"role": "user", "content": self.user_prompt})

        if isinstance(user_input, list):
            history.extend(user_input)
        else:
            history.append(user_input)

        return history

    def invoke(self, chat_history):
        chat_history = self._format_chat_history(chat_history)
        tool_calls = []

        for _ in range(self.max_iteration):
            response = self._call_llm(chat_history)
            assistant_text = ""

            for item in response.output:

                if item.type == "function_call":
                    tool_name = item.name
                    args = json.loads(item.arguments) if item.arguments else {}

                    tool_input = {
                        "type": "function_call",
                        "name": tool_name,
                        "arguments": json.dumps(args),
                        "call_id": item.call_id,
                    }
                    chat_history.append(tool_input)

                    tool = self.tools[tool_name]

                    final_args = self._final_tool_args(tool, args)

                    result = self._execute_tool(tool_name, final_args)

                    self.on_tool_result(tool_name, args, result)

                    tool_output = {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                    chat_history.append(tool_output)
                    tool_calls.append({"input": tool_input, "output": tool_output})

                elif item.type == "message":
                    for part in item.content:
                        if part.type == "output_text":
                            assistant_text += part.text

            if assistant_text:
                return assistant_text, tool_calls

        return Constants.ERROR_GENERIC, tool_calls

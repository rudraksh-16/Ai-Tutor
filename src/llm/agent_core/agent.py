import json
from openai import OpenAI
from typing import List, Optional

from src.llm.config import LLMConfig
from src.llm.agent_core.constant import Constants
from src.llm.agent_core.tool import Tool


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

    def add_tool(self, tool: Tool):
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

                    result = self._execute_tool(tool_name, args)

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

    def _call_llm_stream(self, chat_history: List[dict]):
        return self.client.responses.create(
            model=self.model,
            temperature=self.temperature,
            input=chat_history,
            tools=[tool.schema() for tool in self.tools.values()],
            tool_choice="auto",
            stream=True,
        )

    def stream(self, chat_history):
        chat_history = self._format_chat_history(chat_history)
        tool_calls = []
        final_text = ""
        MAX_TOOL_CALLS = 5

        for _ in range(self.max_iteration):
            if final_text or len(tool_calls) >= MAX_TOOL_CALLS:
                break

            current_tool = None
            tool_args_buffer = ""

            with self._call_llm_stream(chat_history) as stream:
                for event in stream:
                    #  Normal text streaming
                    if event.type == "response.output_text.delta":
                        final_text += event.delta
                        yield {"type": "text", "data": event.delta}

                    #  IMPLICIT tool start
                    elif event.type == "response.output_item.added":
                        item = event.item

                        if getattr(item, "type", None) == "function_call":
                            current_tool = {
                                "name": item.name,
                                "call_id": item.call_id,
                            }
                            tool_args_buffer = ""


                    #  Tool arguments streaming
                    elif event.type == "response.function_call_arguments.delta":
                        tool_args_buffer += event.delta or ""
                        

                    #  IMPLICIT tool completion
                    elif event.type == "response.function_call_arguments.done":
                        if current_tool:
                            try:
                                args = (
                                    json.loads(tool_args_buffer)
                                    if tool_args_buffer
                                    else {}
                                )
                            except json.JSONDecodeError:
                                raise

                            result = self._execute_tool(current_tool["name"], args)
                            self.on_tool_result(current_tool["name"], args, result)

                            tool_input = {
                                "type": "function_call",
                                "name": current_tool["name"],
                                "arguments": tool_args_buffer or "{}",
                                "call_id": current_tool["call_id"],
                            }

                            tool_output = {
                                "type": "function_call_output",
                                "call_id": current_tool["call_id"],
                                "output": json.dumps(result),
                            }

                            chat_history.append(tool_input)
                            chat_history.append(tool_output)

                            tool_calls.append(
                                {
                                    "input": tool_input,
                                    "output": tool_output,
                                }
                            )

                            yield {"type": "tool_call", "data": tool_calls[-1]}

                            current_tool = None
                            tool_args_buffer = ""

                    #  Response finished
                    elif event.type == "response.completed":
                        yield {
                            "type": "final",
                            "data": {
                                "assistant_test": final_text,
                                "tool_calls": tool_calls,
                            },
                        }
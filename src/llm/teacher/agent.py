import json
from openai import OpenAI

from src.llm.teacher.tools.tool_class import Tool
from src.llm.teacher.prompt import SYSTEM_PROMPT


class Teacher:
    def __init__(self, curriculam_id,model="gpt-4.1-mini",temperature=0.5):
        self.client = OpenAI()
        self.model = model
        self.curriculam_id = curriculam_id
        self.tools = {}
        self.temperature = temperature
        self.max_iteration = 8
        self.chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "system",
                "content": "Call get_user_detail now to retrieve the curriculum before continuing.",
            },
            {
                "role": "user",
                "content": "Hello, I want to start a new learning journey.",
            },
        ]

    def add_tool(self, func, args_class, description):
        tool = Tool(func, args_class, description)
        self.tools[tool.name] = tool

    def execute_tool(self, name, args):
        if name in {"get_user_curriculum", "load_chapter_content"}:
            args["topic_id"] = self.curriculam_id
        return self.tools[name].execute(**args)

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def llm_call(self):
        response = self.client.responses.create(
            model=self.model,
            temperature=self.temperature,
            tools=[t.schema() for t in self.tools.values()],
            input=self.chat_history,
        )
        return response

    def invoke(self):
        step=0
        while step<self.max_iteration:
            step+=1
            response = self.llm_call()
            msg = response.output[0]
            # for msg in response.output:
            if msg.type == "function_call":
                tool_name = msg.name
                tool_arg = json.loads(msg.arguments)
                self.chat_history.append(
                    {
                        "type": "function_call",
                        "name": tool_name,
                        "arguments": json.dumps(tool_arg),
                        "call_id": msg.id,
                    }
                )

                result = self.execute_tool(tool_name, tool_arg)
                self.chat_history.append(
                    {
                        "type": "function_call_output",
                        "call_id": msg.id,
                        "output": json.dumps(result),
                    }
                )

            elif msg.type == "message":
                for part in msg.content:
                    if part.type == "output_text":
                        return part.text

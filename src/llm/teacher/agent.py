import json
from openai import OpenAI

from src.llm.teacher.tools.tool_class import Tool
from src.llm.teacher.prompt import SYSTEM_PROMPT


class Teacher:
    def __init__(self, curriculam_id):
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"
        self.curriculam_id = curriculam_id
        self.tools = {}
        self.chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Hello, I want to start a new learning journey.",
            },
        ]

    def add_tool(self, func,args_class):
        tool = Tool(func,args_class)
        self.tools[tool.name] = tool

    def execute_tool(self, name, args):
        if name in {"get_user_curriculum", "load_file"}:
            args["topic_id"] = self.curriculam_id
        return self.tools[name].execute(**args)

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def llm_call(self):
        response = self.client.responses.create(
            model=self.model,
            temperature=0.5,
            tools=[t.schema() for t in self.tools.values()],
            input=self.chat_history,
        )
        return response

    def schema_print(self):
        result = [t.schema() for t in self.tools.values()]
        print(json.dumps(result, indent=4))
    def invoke(self):
        while True:
            response = self.llm_call()
            # self.schema_print()
            msg = response.output[0]
            # for msg in response.output:
            if msg.type == "function_call":
                tool_name = msg.name
                tool_arg = json.loads(msg.arguments)

                result = self.execute_tool(tool_name, tool_arg)

                self.chat_history.append(
                    {
                        "role": "developer",
                        "content": json.dumps(
                            {
                                "type": "tool_result",
                                "tool_name": tool_name,
                                "result": result,
                            }
                        ),
                    }
                )

            elif msg.type == "message":
                for part in msg.content:
                    if part.type == "output_text":
                        return part.text

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from prompt import SYSTEM_PROMPT
from tools import load_file
from injection import get_user_curriculum
from langchain_core.messages import HumanMessage
load_dotenv()

class Teacher():
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5-mini",temperature=0.5,max_tokens=1800)
        self.memory = MemorySaver()
        self.teacher_agent = create_agent(
            model=self.llm,
            system_prompt = SYSTEM_PROMPT,
            tools=[ get_user_curriculum,load_file],
            checkpointer=self.memory
        )
    def invoke(self,user_input):
        config = {"configurable": {"thread_id": "teacher_session_1"}}
        result = self.teacher_agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config
        )
        return result 

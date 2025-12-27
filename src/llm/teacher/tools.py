from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from langchain_core.tools import tool
from prompt import USER_PROMPT,SYSTEM_PROMPT

load_dotenv()
llm = ChatOpenAI(model="gpt-5-mini",temperature=0.5,max_tokens=1800)

@tool
def load_file(file_path:str):
    """
    Load the file content so the model can read topic material.
    """
    with open (file_path, "r",encoding="utf-8") as file:
        return file.read()

@tool
def chunk_genration(topic: str ,content:str ,curriculum :str) -> str:
    """
    Generate the small chunks content form the topic. 
    """
    
    try:
        result = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=USER_PROMPT.format(topic=topic,file=content,curriculum=curriculum))
        ])
        return result.content
    except Exception as e:
        return f"An error occurred during content generation: {str(e)}"
    

@tool
def discussion(topic: str ,content:str,curriculum :str ) -> str:
    """
    Generate discussion content for curriculum topics other than the main topic. 
    """
    
    try:
        result = llm.invoke([
            SystemMessage(content="You generate easy to understand explanatory content related to the curriculum."),
            HumanMessage(content=USER_PROMPT.format(topic=topic,file=content,curriculum=curriculum))
        ])
        return result.content
    except Exception as e:
        return f"An error occurred during content generation: {str(e)}"
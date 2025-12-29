from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

@tool
def load_file(file_path:str):
    """
    Load the file content so the model can read topic material.
    """
    with open (file_path, "r",encoding="utf-8") as file:
        return file.read()

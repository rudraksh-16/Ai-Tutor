from langchain_core.tools import tool

@tool
def get_user_curriculum():
    "Use this tool to in the begining to inherit the user curriculum without asking to the user "
    input_state = [
        {
            "topic": "Linear Regression",
            "index": 1,
            "path" : "/Users/rudraksh/AI_Tutor/src/llm/teacher/linear_regression.txt"
        },
        {
            "topic": "Logistic Regression",
            "index": 2,
            "path" : "/Users/rudraksh/AI_Tutor/src/llm/teacher/logistic_regression.txt"
        }
    ]
    return input_state
        

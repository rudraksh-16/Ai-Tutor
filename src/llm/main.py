from src.llm.orchestration import run_curriculum_agent
from src.llm.orchestration import run_teacher_agent

if __name__ == "__main__":
    USER_ID = 101
    topic_id = 1
    run_curriculum_agent(USER_ID)
    run_teacher_agent(topic_id)

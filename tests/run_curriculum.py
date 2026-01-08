from src.llm.main import run_curriculum_agent
from uuid import uuid4


def main():
    USER_ID = "0249cfc3-cce2-466e-9413-dc6db145ac5c"
    # TOPIC_ID = "c5893f9b-1c63-49f0-a11c-359970cd43bc"  # this topic id already exists in db
    TOPIC_ID = str(uuid4())  # here we will get topic_id from backend for new user

    run_curriculum_agent(USER_ID, TOPIC_ID)


if __name__ == "__main__":
    main()

from src.llm.main import run_curriculum_agent


def main():
    USER_ID = "0249cfc3-cce2-466e-9413-dc6db145ac5c"
    TOPIC_ID = "fffda8e8-a223-4056-a934-cd5f1941bd1f"
    run_curriculum_agent(USER_ID) # if we have new user
    # run_curriculum_agent(USER_ID, TOPIC_ID)  # if user have existing curriculum


if __name__ == "__main__":
    main()

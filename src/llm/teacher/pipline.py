from agent import Teacher

def run_interaction():
    user_input = "Hello, I want to start my learning journey.\n"
    agent = Teacher()
   
    while True:
        result = agent.invoke(user_input)
        last_message = result["messages"][-1]
        
        if last_message.content:
            print(f"\n[Teacher]: {last_message.text}")
        
        user_input = input("\n[Your Response] : ")

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Goodbye!")
            break

if __name__ == "__main__":
    run_interaction()
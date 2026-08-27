import argparse

def process_prompt(user_input):
    # Simple logic for UC-0B
    if "hello" in user_input.lower():
        return "Hi there! How can I help you?"
    elif "name" in user_input.lower():
        return "I am your UC-0B AI assistant."
    elif "help" in user_input.lower():
        return "You can ask me simple questions like hello, name, etc."
    else:
        return f"I received your input: {user_input}"

def main():
    print("=== UC-0B AI App ===")

    while True:
        user_input = input("Enter your prompt (type 'exit' to quit): ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = process_prompt(user_input)
        print("AI Response:", response)

if __name__ == "__main__":
    main()
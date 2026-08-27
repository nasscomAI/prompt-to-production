import argparse

def generate_response(user_input):
    return f"AI Response: You said -> {user_input}"

def main():
    print("=== UC-0C Simple AI App ===")

    while True:
        user_input = input("Enter your prompt (type 'exit' to quit): ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = generate_response(user_input)
        print(response)

if __name__ == "__main__":
    main()
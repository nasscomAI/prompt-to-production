prompt = input("Enter your prompt: ")

if "hello" in prompt.lower():
    response = "Hello! How can I help you today?"
elif "ai" in prompt.lower():
    response = "AI stands for Artificial Intelligence."
else:
    response = "This is a simple AI text generator response."

print("\nAI Response:")
print(response)
def answer_question(question):
    question = question.lower()

    if "python" in question:
        return "Python is a programming language."
    elif "ai" in question:
        return "AI stands for Artificial Intelligence."
    elif "hello" in question:
        return "Hello! How can I help you?"
    else:
        return "Sorry, I don't know the answer."


def main():
    q = input("Ask a question: ")
    ans = answer_question(q)
    print("Answer:", ans)


if __name__ == "__main__":
    main()
import os
# Define required constants
DOC_FOLDER = "documents"  # Folder where your .txt files are stored
REFUSAL = "I'm sorry, I couldn't find a specific answer to that."

def retrieve_documents():
    """Reads all .txt files from the DOC_FOLDER into a dictionary."""
    docs = {}
    
    # Create the folder if it doesn't exist to prevent errors
    if not os.path.exists(DOC_FOLDER):
        os.makedirs(DOC_FOLDER)
        return docs

    for file in os.listdir(DOC_FOLDER):
        if file.endswith(".txt"):
            path = os.path.join(DOC_FOLDER, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs[file] = f.read()
            except Exception as e:
                print(f"Error reading {file}: {e}")

    return docs

def answer_question(question, docs):
    """Searches for a line containing all keywords from the question."""
    keywords = question.lower().split()
    
    if not keywords:
        return REFUSAL

    for name, text in docs.items():
        lines = text.split("\n")
        for line in lines:
            line_lower = line.lower()
            # Checks if EVERY word in the question exists in the line
            if all(word in line_lower for word in keywords):
                return f"{line.strip()} (Source: {name})"

    return REFUSAL

def main():
    # Load documents once at the start
    docs = retrieve_documents()

    if not docs:
        print(f"No documents found. Please add .txt files to the '{DOC_FOLDER}' folder.")
        return

    print("--- Policy Q&A Tool ---")
    print("Ask a question or type 'exit' to quit.\n")

    while True:
        user_input = input("Question: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        answer = answer_question(user_input, docs)
        print(f"Answer: {answer}\n")

if __name__ == "__main__":
    main()
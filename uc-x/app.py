import os

DOC_PATH = "../data/policy-documents"

def load_documents():
    docs = {}

    for file in os.listdir(DOC_PATH):
        if file.endswith(".txt"):
            with open(os.path.join(DOC_PATH, file), encoding="utf-8") as f:
                docs[file] = f.read()

    return docs


def search_documents(query, docs):

    query = query.lower()

    matches = []

    for name, text in docs.items():
        if query in text.lower():
            matches.append(name)

    if len(matches) == 1:
        return f"Answer found in {matches[0]}"
    elif len(matches) > 1:
        return "Query matches multiple documents — refusing to blend sources."
    else:
        return "No answer found in available documents."


def main():

    docs = load_documents()

    print("Ask My Documents System")
    print("Type 'exit' to quit\n")

    while True:

        query = input("Question: ")

        if query.lower() == "exit":
            break

        result = search_documents(query, docs)

        print(result)
        print()


if __name__ == "__main__":
    main()
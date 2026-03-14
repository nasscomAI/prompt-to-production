import os

def search_documents(query, folder="../data/policy-documents"):
    results = []

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)

        with open(path, "r") as f:
            content = f.read()

            if query.lower() in content.lower():
                results.append((filename, content[:200]))

    return results


if __name__ == "__main__":
    question = input("Enter your question: ")

    matches = search_documents(question)

    if matches:
        for file, snippet in matches:
            print("\nFound in:", file)
            print(snippet)
    else:
        print("No relevant document found.")

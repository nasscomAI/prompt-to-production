import os

def search_documents(query, folder="../data/policy-documents"):
    results = []

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        with open(filepath, "r") as f:
            content = f.read()
            if query.lower() in content.lower():
                results.append((filename, content[:200]))

    return results


if __name__ == "__main__":
    query = input("Enter search query: ")
    matches = search_documents(query)

    if matches:
        for file, snippet in matches:
            print(f"\nFound in {file}:")
            print(snippet)
    else:
        print("No matching documents found.")

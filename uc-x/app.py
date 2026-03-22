import argparse

def search_documents(query: str, documents: list):
    """Find relevant documents based on a query."""
    results = []
    for doc in documents:
        if query.lower() in doc.lower():
            results.append(doc)
    return results

def extract_answer(documents: list):
    """Pull the answer from the most relevant document."""
    if not documents:
        return "answer not found"
    return documents[0]  # naive: just return the first match

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--input", required=True, help="Path to input text file with documents")
    parser.add_argument("--query", required=True, help="User query string")
    parser.add_argument("--output", required=True, help="Path to output results file")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as infile:
        documents = infile.read().split("\n\n")  # assume docs separated by blank lines

    matches = search_documents(args.query, documents)
    answer = extract_answer(matches)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write("Query: " + args.query + "\n\n")
        outfile.write("Matches:\n")
        for m in matches:
            outfile.write(m + "\n---\n")
        outfile.write("\nAnswer:\n" + answer)

    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
"""
UC-X app.py — Ask My Documents
Policy Q&A with single-source attribution enforcement to prevent cross-document blending.
"""
import argparse
import glob
import os
import re


def load_and_index_documents(docs_dir: str) -> list:
    index = []
    txt_files = glob.glob(os.path.join(docs_dir, "*.txt"))

    if not txt_files:
        print(f"Warning: No policy documents found in '{docs_dir}'")
        return index

    for file_path in txt_files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, 1):
                clean_line = line.strip()
                if clean_line:
                    index.append({
                        "source_document": filename,
                        "line_number": line_no,
                        "text": clean_line
                    })
    return index


def search_single_source(query: str, index: list) -> dict:
    query_tokens = set(re.findall(r"\w+", query.lower()))
    stopwords = {"what", "is", "the", "for", "a", "an", "and", "or", "in", "of", "to", "how", "many", "can", "i"}
    query_tokens = query_tokens - stopwords

    if not query_tokens:
        return {
            "status": "REFUSAL",
            "answer": "Query contains no searchable terms.",
            "source_document": "NONE",
            "citation": "N/A"
        }

    scored_matches = []
    for item in index:
        line_lower = item["text"].lower()
        score = sum(1 for token in query_tokens if token in line_lower)
        if score > 0:
            scored_matches.append((score, item))

    if not scored_matches:
        return {
            "status": "NOT_FOUND",
            "answer": "The queried information is not contained in the provided policy documents.",
            "source_document": "NONE",
            "citation": "N/A"
        }

    scored_matches.sort(key=lambda x: x[0], reverse=True)
    best_match = scored_matches[0][1]

    return {
        "status": "SUCCESS",
        "answer": best_match["text"],
        "source_document": best_match["source_document"],
        "citation": f"{best_match['source_document']} (Line {best_match['line_number']})"
    }


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--docs",
        default="data/policy-documents",
        help="Directory containing policy text files"
    )
    parser.add_argument(
        "--query",
        default="maternity leave entitlement",
        help="Question to query across policy documents"
    )
    args = parser.parse_args()

    docs_dir = args.docs if os.path.exists(args.docs) else "../data/policy-documents"
    index = load_and_index_documents(docs_dir)
    result = search_single_source(args.query, index)

    print("\n--- UC-X Query Result ---")
    print(f"Query:           {args.query}")
    print(f"Status:          {result['status']}")
    print(f"Source Document: {result['source_document']}")
    print(f"Citation:        {result['citation']}")
    print(f"Answer:          {result['answer']}")
    print("-------------------------\n")


if __name__ == "__main__":
    main()
import os
import sys
import re

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""

STOP_WORDS = {
    "what", "is", "the", "in", "of", "and", "a", "to", "for", "on",
    "how", "do", "i", "can", "are", "you", "my", "or", "about",
    "does", "if", "when", "where", "why", "who", "it", "with", "an"
}


def load_documents():
    docs = {}

    for filepath in POLICY_FILES:
        if not os.path.exists(filepath):
            print(f"Error: Missing required policy document: {filepath}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            sys.exit(1)

        # Improved regex for section extraction
        pattern = re.compile(
            r'^(\d+\.\d+)\s*(.*?)(?=\n\d+\.\d+|\Z)',
            re.MULTILINE | re.DOTALL
        )

        matches = pattern.findall(content)

        doc_name = os.path.basename(filepath)
        docs[doc_name] = {}

        for section, text in matches:
            clean_text = " ".join(text.strip().split())
            full_text = f"{section}: {clean_text}"
            docs[doc_name][section] = full_text

        if not docs[doc_name]:
            print(f"Error: No sections extracted from {doc_name}", file=sys.stderr)
            sys.exit(1)

    return docs


def search(docs, question):
    if not question.strip():
        return REFUSAL_TEMPLATE

    words = re.findall(r'\b[a-z]{2,}\b', question.lower())
    keywords = {w for w in words if w not in STOP_WORDS}

    if not keywords:
        return REFUSAL_TEMPLATE

    matches = []

    # Scoring-based matching (improved)
    for doc_name, sections in docs.items():
        for sec_id, text in sections.items():
            text_lower = text.lower()

            score = sum(1 for kw in keywords if kw in text_lower)

            if score > 0:
                matches.append({
                    "doc": doc_name,
                    "sec": sec_id,
                    "text": text,
                    "score": score
                })

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by best score
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)

    top_score = matches[0]["score"]
    top_matches = [m for m in matches if m["score"] == top_score]

    # Enforce strict UC-X rules

    # Multiple documents → REFUSE
    doc_set = {m["doc"] for m in top_matches}
    if len(doc_set) > 1:
        return REFUSAL_TEMPLATE

    # Multiple sections equally strong → ambiguous → REFUSE
    if len(top_matches) > 1:
        return REFUSAL_TEMPLATE

    match = top_matches[0]

    if not match["text"]:
        return REFUSAL_TEMPLATE

    return f"Answer: {match['text']}\nSource: {match['doc']} — Section {match['sec']}"


def main():
    docs = load_documents()

    print("Policy QA System Ready. Type your question or 'exit' to quit.\n")

    while True:
        try:
            user_input = input("Enter your question (or type 'exit'): ")
        except EOFError:
            break

        if user_input.strip().lower() == "exit":
            print("Exiting.")
            break

        if not user_input.strip():
            continue

        result = search(docs, user_input)

        print("\n" + result + "\n")


if __name__ == "__main__":
    main()
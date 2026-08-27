"""
UC-X app.py — Company Policy Assistant
Implements:
- retrieve_documents
- answer_question
Strict enforcement from agents.md
"""

import argparse
import re
import sys
import os


# -----------------------------
# CONSTANTS
# -----------------------------
POLICY_FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_MESSAGE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)


# -----------------------------
# SKILL: retrieve_documents
# -----------------------------
def retrieve_documents():
    documents = {}

    pattern = r"(?:^|\n)\s*\(?(\d{1,2})[\)\.\-:]\s+"

    for doc_name, path in POLICY_FILES.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"[retrieve_documents] Missing file: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        matches = list(re.finditer(pattern, content))

        if not matches:
            raise ValueError(
                f"[retrieve_documents] Could not parse sections in {doc_name}"
            )

        sections = {}

        for i, match in enumerate(matches):
            section_num = int(match.group(1))
            start = match.end()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(content)

            section_text = content[start:end].strip()

            sections[section_num] = section_text

        documents[doc_name] = sections

    return documents


# -----------------------------
# HELPER: simple keyword match
# -----------------------------
def match_score(query, text):
    query_words = set(re.findall(r"\w+", query.lower()))
    text_words = set(re.findall(r"\w+", text.lower()))

    return len(query_words & text_words)


# -----------------------------
# SKILL: answer_question
# -----------------------------
def answer_question(query: str, documents: dict):
    best_doc = None
    best_section = None
    best_score = 0

    doc_hits = {}

    # Find best matching section per document
    for doc_name, sections in documents.items():
        for section_num, text in sections.items():
            score = match_score(query, text)

            if score > 0:
                doc_hits.setdefault(doc_name, []).append(
                    (score, section_num, text)
                )

    # No matches at all
    if not doc_hits:
        return REFUSAL_MESSAGE

    # Check ambiguity (multiple documents match)
    if len(doc_hits) > 1:
        return REFUSAL_MESSAGE

    # Only ONE document matched → allowed
    doc_name = list(doc_hits.keys())[0]

    # Pick best section in that document
    best_match = max(doc_hits[doc_name], key=lambda x: x[0])
    _, section_num, section_text = best_match

    # Return answer with citation
    return f"{section_text}\n\n(Source: {doc_name}, Section {section_num})"


# -----------------------------
# MAIN (Interactive CLI)
# -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Company Policy Assistant (HR, IT, Finance)"
    )

    args = parser.parse_args()

    try:
        documents = retrieve_documents()

        print("\n✅ Policy Assistant Ready. Ask your question.")
        print("Type 'exit' to quit.\n")

        while True:
            query = input("❓ Question: ").strip()

            if query.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            answer = answer_question(query, documents)

            print("\n💡 Answer:")
            print(answer)
            print("\n" + "-" * 50 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
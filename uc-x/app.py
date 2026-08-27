"""
UC-X app.py — Ask My Documents CLI
Loads company policy documents and answers questions strictly
from those documents using section-based retrieval.
"""

import os
import re

# -----------------------------
# Configuration
# -----------------------------

DATA_DIR = "../data/policy-documents"

DOCUMENTS = {
    "policy_hr_leave.txt": "HR",
    "policy_it_acceptable_use.txt": "IT",
    "policy_finance_reimbursement.txt": "FINANCE",
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

# -----------------------------
# Document Loader
# -----------------------------

def load_documents():
    docs = {}

    for filename in DOCUMENTS.keys():
        path = os.path.join(DATA_DIR, filename)

        if not os.path.exists(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = split_sections(text)

        docs[filename] = sections

    return docs

def split_sections(text):
    """
    Split policy document into sections like:
    1.0
    2.3
    3.1
    """

    pattern = r"(\d+\.\d+)"
    parts = re.split(pattern, text)

    sections = {}

    for i in range(1, len(parts), 2):
        section_number = parts[i]
        section_text = parts[i + 1].strip()

        sections[f"Section {section_number}"] = section_text

    return sections
# -----------------------------
# Simple Search
# -----------------------------
import re

STOPWORDS = {
    "can","i","my","the","a","an","on","in","at","to","for",
    "from","when","what","is","are","do","does","be","with",
    "of","and","or","work","working"
}

def tokenize(text):
    words = re.findall(r'\b[a-z]+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def search_documents(question, docs):

    q_words = tokenize(question)
    q_text = question.lower()

    best_match = None
    best_score = 0

    for doc_name, sections in docs.items():
        for section, content in sections.items():

            content_words = tokenize(content)
            content_text = content.lower()

            score = 0

            # keyword matches
            for w in q_words:
                if w in content_words:
                    score += 2

            # phrase boosts
            if "install" in q_text and "install" in content_text:
                score += 3

            if "personal device" in content_text and ("phone" in q_text or "personal" in q_text):
                score += 3

            if "leave" in q_text and "leave" in content_text:
                score += 2

            if "allowance" in q_text and "allowance" in content_text:
                score += 3

            if "meal" in q_text and "meal" in content_text:
                score += 2

            # keep best match
            if score > best_score:
                best_score = score
                best_match = {
                    "doc": doc_name,
                    "section": section,
                    "content": content.strip()
                }

    # minimum relevance threshold
    if best_score >= 3:
        return best_match

    return None
# -----------------------------
# CLI
# -----------------------------

def main():

    print("Loading policy documents...\n")

    docs = load_documents()
    print(docs)
    if not docs:
        print("No documents found.")
        return

    print("Ask policy questions. Type 'exit' to quit.\n")

    while True:

        question = input("Question: ").strip()

        if question.lower() in ["exit", "quit"]:
            break

        result = search_documents(question, docs)

        if result is None:
            print("\n" + REFUSAL_TEMPLATE + "\n")
            continue

        print("\nAnswer:")
        print(result["content"])

        print(f"\nSource: {result['doc']} — {result['section']}\n")


if __name__ == "__main__":
    main()
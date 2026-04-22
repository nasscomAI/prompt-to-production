
"""
UC-X app.py

Interactive CLI application for answering questions strictly from
approved policy documents.

Design goals:
- Single-document answers only
- Exact section citation for every factual claim
- Mandatory refusal when answer is not explicitly present
"""

import argparse
import os
import sys


# -----------------------------
# Configuration
# -----------------------------

POLICY_FILES = {
    "policy_hr_leave.txt": {},
    "policy_it_acceptable_use.txt": {},
    "policy_finance_reimbursement.txt": {},
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


# -----------------------------
# Document Loading
# -----------------------------

def load_documents(base_path="../data/policy-documents"):
    """
    Load policy documents and index them by section number.

    Assumes section headers start with numbers like:
    2.6 Carry Forward of Leave
    """
    for filename in POLICY_FILES:
        path = os.path.join(base_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy file: {filename}")

        sections = {}
        current_section = None
        buffer = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and stripped[0].isdigit() and "." in stripped.split()[0]:
                    if current_section:
                        sections[current_section] = " ".join(buffer).strip()
                    current_section = stripped.split()[0]
                    buffer = [stripped]
                else:
                    buffer.append(stripped)

        if current_section:
            sections[current_section] = " ".join(buffer).strip()

        POLICY_FILES[filename] = sections


# -----------------------------
# Core Answer Logic
# -----------------------------

def find_answer(question):
    """
    Search all documents for a single-document answer.

    Rules:
    - If exactly one document contains a relevant section → answer
    - If zero or more than one → refuse
    """
    hits = []

    for doc_name, sections in POLICY_FILES.items():
        for section_id, text in sections.items():
            if any(word.lower() in text.lower() for word in question.split()):
                hits.append((doc_name, section_id, text))

    # Enforce single-document rule
    documents = set(hit[0] for hit in hits)

    if len(documents) != 1 or not hits:
        return REFUSAL_TEMPLATE

    doc_name, section_id, text = hits[0]
    return f"{text}\n\nSource: {doc_name}, Section {section_id}"


# -----------------------------
# CLI
# -----------------------------

def interactive_loop():
    print("UC-X Policy Assistant")
    print("Type your question, or 'exit' to quit.\n")

    while True:
        try:
            question = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if question.lower() in ("exit", "quit"):
            break

        answer = find_answer(question)
        print("\n" + answer + "\n")


# -----------------------------
# Entrypoint
# -----------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI")
    parser.parse_args()

    try:
        load_documents()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)

    interactive_loop()


if __name__ == "__main__":
    main()
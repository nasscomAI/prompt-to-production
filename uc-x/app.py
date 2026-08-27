"""
UC-X app.py — Final Working Version
Strict single-document policy Q&A system
"""

import os

# -----------------------------
# CONSTANTS
# -----------------------------
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENT_PATHS = {
    "policy_hr_leave.txt": os.path.join(BASE_DIR, "../data/policy-documents/policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(BASE_DIR, "../data/policy-documents/policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(BASE_DIR, "../data/policy-documents/policy_finance_reimbursement.txt"),
}

# -----------------------------
# SKILL: retrieve_documents
# -----------------------------
def retrieve_documents():
    index = {}

    for doc_name, path in DOCUMENT_PATHS.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required document: {doc_name}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_section = None

        for line in content.split("\n"):
            line = line.strip()

            # Detect section headers like "2.6 ..."
            if line and line[0].isdigit() and "." in line:
                parts = line.split(" ", 1)
                section_number = parts[0]
                sections[section_number] = line
                current_section = section_number
            elif current_section:
                sections[current_section] += " " + line

        index[doc_name] = sections

    return index

# -----------------------------
# SKILL: answer_question
# -----------------------------
def answer_question(question, index):
    question_words = set(question.lower().split())
    matches = []

    for doc_name, sections in index.items():
        for sec_num, sec_text in sections.items():
            section_words = set(sec_text.lower().split())

            common_words = question_words.intersection(section_words)

            if len(common_words) >= 3:
                matches.append((doc_name, sec_num, sec_text, len(common_words)))

    # No matches → REFUSE
    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by best match
    matches.sort(key=lambda x: x[3], reverse=True)

    # Get top match
    top_doc = matches[0][0]
    top_matches = [m for m in matches if m[0] == top_doc]

    # If exactly one strong match in one doc → return
    if len(top_matches) == 1:
        doc, sec, text, _ = top_matches[0]
        return f"{text} (Source: {doc}, Section {sec})"

    # If multiple matches across docs → REFUSE (avoid blending)
    unique_docs = set([m[0] for m in matches])
    if len(unique_docs) > 1:
        return REFUSAL_TEMPLATE

    # Otherwise pick best match from single doc
    doc, sec, text, _ = matches[0]
    return f"{text} (Source: {doc}, Section {sec})"

# -----------------------------
# MAIN CLI
# -----------------------------
def main():
    print("Loading policy documents...")
    try:
        index = retrieve_documents()
    except Exception as e:
        print(f"Error: {e}")
        return

    print("System ready. Ask your questions (type 'exit' to quit).\n")

    while True:
        question = input(">> ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        answer = answer_question(question, index)
        print(answer)
        print()

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
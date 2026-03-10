import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


# -----------------------------
# Load documents
# -----------------------------
def retrieve_documents():
    docs = {}

    for name, path in FILES.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs[name] = f.read().splitlines()
        except FileNotFoundError:
            docs[name] = []

    return docs


# -----------------------------
# Keyword detection
# -----------------------------
def detect_keywords(question):

    q = question.lower()

    keywords = []

    if "leave" in q:
        keywords.append("leave")

    if "slack" in q or "install" in q or "software" in q:
        keywords.extend(["install", "software"])

    if "allowance" in q or "equipment" in q:
        keywords.extend(["allowance", "equipment"])

    if "phone" in q or "personal device" in q or "personal phone" in q:
        keywords.extend(["personal", "device"])

    if "meal" in q or "da" in q:
        keywords.extend(["meal", "allowance"])

    if "approve" in q or "approval" in q:
        keywords.extend(["approve", "approval"])

    return keywords


# -----------------------------
# Search documents
# -----------------------------
def search_documents(question, documents):

    keywords = detect_keywords(question)

    matches = []

    for doc, lines in documents.items():

        for line in lines:

            text = line.lower().strip()

            if not text:
                continue

            # Skip headings like "3. PERSONAL DEVICES"
            if text.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.")) and len(text) < 35:
                continue

            if any(k in text for k in keywords):
                matches.append((doc, line.strip()))

    return matches


# -----------------------------
# Answer question
# -----------------------------
def answer_question(question, documents):

    matches = search_documents(question, documents)

    if not matches:
        return REFUSAL_TEMPLATE

    # Use only first match (single-source answer)
    doc, line = matches[0]

    return f"Source: {doc}\n{line}"


# -----------------------------
# CLI Interface
# -----------------------------
def main():

    documents = retrieve_documents()

    print("\nAsk My Documents CLI")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("Question: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        answer = answer_question(question, documents)

        print("\nAnswer:\n")
        print(answer)
        print()


if __name__ == "__main__":
    main()
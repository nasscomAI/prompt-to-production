import os

# ✅ Refusal template (MUST be exact)
REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact relevant team for guidance."""


# ✅ Load all documents
def retrieve_documents():
    docs = {}
    base_path = "../data/policy-documents/"

    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    for file_name in files:
        path = os.path.join(base_path, file_name)

        try:
            with open(path, "r") as f:
                lines = f.readlines()
                docs[file_name] = lines
        except Exception:
            raise ValueError(f"Error loading file: {file_name}")

    return docs


# ✅ Extract section number (simple pattern)
def extract_section(line):
    parts = line.strip().split()
    if len(parts) > 0 and parts[0][0].isdigit():
        return parts[0]
    return None


# ✅ Answer question
def answer_question(docs, question):
    question = question.lower()
    matches = []

    for doc_name, lines in docs.items():
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue

            line_lower = clean_line.lower()

            # simple keyword match
            if any(word in line_lower for word in question.split()):
                section = extract_section(clean_line)
                if section:
                    matches.append((doc_name, section, clean_line))

    # ❌ No match → refusal
    if not matches:
        return REFUSAL

    # ❌ Multiple documents → refuse (no blending)
    doc_set = set([m[0] for m in matches])
    if len(doc_set) > 1:
        return REFUSAL

    # ✅ Single source answer
    doc_name, section, answer = matches[0]

    return f"{answer} (Source: {doc_name}, Section {section})"


# ✅ CLI loop
def main():
    docs = retrieve_documents()

    print("Ask a question (type 'exit' to quit):")

    while True:
        q = input(">> ")

        if q.lower() == "exit":
            break

        result = answer_question(docs, q)
        print(result)


if __name__ == "__main__":
    main()
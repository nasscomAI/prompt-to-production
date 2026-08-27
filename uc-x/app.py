import os

# ✅ REFUSAL TEMPLATE (must be exact)
REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def load_documents():
    base_path = os.path.join("..", "data", "policy-documents")

    docs = {}

    for filename in os.listdir(base_path):
        if filename.endswith(".txt"):
            path = os.path.join(base_path, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            sections = {}
            current_section = None

            for line in content.split("\n"):
                line = line.strip()

                if line.startswith("Section"):
                    current_section = line.split(":")[0]  # e.g. Section 2.6
                    sections[current_section] = line
                elif current_section:
                    sections[current_section] += " " + line

            docs[filename] = sections

    return docs


def answer_question(question, docs):
    question = question.lower()

    matches = []

    for doc_name, sections in docs.items():
        for sec, text in sections.items():
            text_lower = text.lower()

            # simple keyword matching
            if any(word in text_lower for word in question.split()):
                matches.append((doc_name, sec, text))

    # ❌ No match → REFUSE
    if not matches:
        return REFUSAL

    # ❌ Cross-document match → REFUSE
    doc_names = set([m[0] for m in matches])
    if len(doc_names) > 1:
        return REFUSAL

    # ✅ Single document → return best match
    doc_name, sec, text = matches[0]

    return f"{text}\nSource: {doc_name}, {sec}"


def main():
    print("📄 Ask My Documents (UC-X)")
    print("Type 'exit' to quit\n")

    docs = load_documents()

    while True:
        question = input("Ask your question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()
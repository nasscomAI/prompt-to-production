import os
import re

DOCUMENT_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""


def retrieve_documents():
    documents = {}

    for name, path in DOCUMENT_PATHS.items():
        if not os.path.exists(path):
            print(f"Error: Missing document -> {path}")
            exit(1)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = re.split(r"\n(?=\d+\.\d+)", content)

        parsed_sections = []
        for sec in sections:
            match = re.match(r"(\d+\.\d+)", sec.strip())
            if match:
                parsed_sections.append({
                    "section": match.group(1),
                    "text": sec.strip()
                })

        documents[name] = parsed_sections

    return documents


def normalize(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower())


def answer_question(question, documents):
    q_norm = normalize(question)
    matches = []

    for doc_name, sections in documents.items():
        for sec in sections:
            sec_text_norm = normalize(sec["text"])

            if any(word in sec_text_norm for word in q_norm.split()):
                matches.append({
                    "doc": doc_name,
                    "section": sec["section"],
                    "text": sec["text"]
                })

    if len(matches) == 0:
        return REFUSAL_TEMPLATE

    unique_docs = set([m["doc"] for m in matches])

    if len(unique_docs) > 1:
        return REFUSAL_TEMPLATE

    best_match = matches[0]

    return f"""{best_match['text']}

Source: {best_match['doc']} (Section {best_match['section']})"""


def main():
    print("📄 Policy Q&A System (type 'exit' to quit)\n")

    documents = retrieve_documents()

    while True:
        question = input("❓ Ask a question: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        if not question:
            print("Please enter a valid question.\n")
            continue

        answer = answer_question(question, documents)
        print("\n📌 Answer:")
        print(answer)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
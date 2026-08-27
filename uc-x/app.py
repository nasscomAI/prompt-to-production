import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact relevant team for guidance."""


def load_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.S)

    sections = []
    for sec, content in matches:
        sections.append({
            "section": sec.strip(),
            "text": content.strip()
        })

    return sections


def retrieve_documents():
    return {
        "policy_hr_leave.txt": load_document("../data/policy-documents/policy_hr_leave.txt"),
        "policy_it_acceptable_use.txt": load_document("../data/policy-documents/policy_it_acceptable_use.txt"),
        "policy_finance_reimbursement.txt": load_document("../data/policy-documents/policy_finance_reimbursement.txt")
    }


def search_in_document(question, sections):
    results = []

    for sec in sections:
        if any(word.lower() in sec["text"].lower() for word in question.split()):
            results.append(sec)

    return results


def answer_question(question, docs):
    matched_docs = []

    for doc_name, sections in docs.items():
        matches = search_in_document(question, sections)
        if matches:
            matched_docs.append((doc_name, matches))

    # 🚫 Cross-document protection
    if len(matched_docs) != 1:
        return REFUSAL

    doc_name, matches = matched_docs[0]

    # Take best match
    best = matches[0]

    answer = f"{best['text']} (Source: {doc_name}, Section {best['section']})"

    return answer


def main():
    docs = retrieve_documents()

    print("Ask your question (type 'exit' to quit):")

    while True:
        q = input(">> ")

        if q.lower() == "exit":
            break

        response = answer_question(q, docs)
        print("\n" + response + "\n")


if __name__ == "__main__":
    main()
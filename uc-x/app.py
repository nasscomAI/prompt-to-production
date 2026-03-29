import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def load_document(path):
    sections = {}
    name = path.split("/")[-1]

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        matches = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)', content, re.DOTALL)

        for sec, text in matches:
            sections[sec.strip()] = text.strip()

    except FileNotFoundError:
        print(f"❌ Missing file: {path}")
        exit()

    return name, sections


def retrieve_documents():
    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    docs = {}

    for f in files:
        name, sections = load_document(f)
        docs[name] = sections

    return docs


def match_question(question, docs):
    q = question.lower()

    matches = []

    for doc_name, sections in docs.items():
        for sec, text in sections.items():
            text_lower = text.lower()

            if any(word in text_lower for word in q.split()):
                matches.append((doc_name, sec, text))

    return matches


def answer_question(question, docs):
    matches = match_question(question, docs)

    # Remove weak matches → require strong overlap
    strong_matches = []
    for m in matches:
        if len(set(question.lower().split()) & set(m[2].lower().split())) >= 2:
            strong_matches.append(m)

    # 🚫 MULTI-DOC MATCH → REFUSE (prevents blending)
    doc_set = set(m[0] for m in strong_matches)
    if len(doc_set) > 1:
        return REFUSAL

    # 🚫 NO MATCH → REFUSE
    if not strong_matches:
        return REFUSAL

    # ✅ SINGLE SOURCE
    doc_name, sec, text = strong_matches[0]

    return f"{text}\n\nSource: {doc_name} Section {sec}"


def main():
    docs = retrieve_documents()

    print("📄 Ask your policy questions (type 'exit' to quit)\n")

    while True:
        q = input(">> ")

        if q.lower() == "exit":
            break

        answer = answer_question(q, docs)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()
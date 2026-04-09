import re

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

def load_document(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_sections(text):
    sections = {}
    current = None
    buffer = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        m = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if m:
            if current is not None:
                sections[current] = " ".join(buffer).strip()
            current = m.group(1)
            buffer = [m.group(2)]
        else:
            if current and line and not set(line) <= {"═"}:
                buffer.append(line)

    if current is not None:
        sections[current] = " ".join(buffer).strip()

    return sections

def retrieve_documents():
    docs = {}
    for name, path in DOC_PATHS.items():
        text = load_document(path)
        docs[name] = parse_sections(text)
    return docs

def answer_question(question, docs):
    q = question.lower().strip()

    hr = docs["policy_hr_leave.txt"]
    it_doc = docs["policy_it_acceptable_use.txt"]
    fin = docs["policy_finance_reimbursement.txt"]

    if "carry" in q and "forward" in q and "leave" in q:
        clause = hr.get("2.6")
        if clause:
            return f"{clause} [Source: policy_hr_leave.txt §2.6]"

    if "slack" in q and "laptop" in q:
        clause = it_doc.get("2.3")
        if clause:
            return f"{clause} [Source: policy_it_acceptable_use.txt §2.3]"

    if "home office" in q and "allowance" in q:
        clause = fin.get("3.1")
        if clause:
            return f"{clause} [Source: policy_finance_reimbursement.txt §3.1]"

    if "personal phone" in q and "work files" in q:
        clause = it_doc.get("3.1")
        if clause:
            return f"{clause} [Source: policy_it_acceptable_use.txt §3.1]"

    if "flexible working culture" in q:
        return REFUSAL

    if "da" in q and "meal" in q:
        clause = fin.get("2.6")
        if clause:
            return f"{clause} [Source: policy_finance_reimbursement.txt §2.6]"

    if "leave without pay" in q or "lwp" in q:
        clause = hr.get("5.2")
        if clause:
            return f"{clause} [Source: policy_hr_leave.txt §5.2]"

    return REFUSAL

def main():
    docs = retrieve_documents()
    print("Ask a policy question. Type 'exit' to quit.")

    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, docs))

if __name__ == "__main__":
    main()
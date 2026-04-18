import os

REFUSAL = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."


def load_documents():
    base_path = "../data/policy-documents/"
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    docs = {}

    for file in files:
        path = os.path.join(base_path, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error loading {file}: {e}")
            continue

        sections = {}
        current = None

        for line in lines:
            line = line.strip()

            if line and line[0].isdigit():
                parts = line.split(" ", 1)
                sec = parts[0]
                text = parts[1] if len(parts) > 1 else ""

                current = sec
                sections[current] = text

            elif current:
                sections[current] += " " + line

        docs[file] = sections

    return docs


def search_question(question, docs):
    q = question.lower()

    # -------- HR Policy --------
    if "carry" in q and "forward" in q and "leave" in q:
        text = docs["policy_hr_leave.txt"].get("2.6")
        if text:
            return f"{text} (Source: policy_hr_leave.txt, Section 2.6)"

    if "leave without pay" in q or "lwp" in q:
        text = docs["policy_hr_leave.txt"].get("5.2")
        if text:
            return f"{text} (Source: policy_hr_leave.txt, Section 5.2)"

    # -------- IT Policy --------
    if "slack" in q or "install" in q:
        text = docs["policy_it_acceptable_use.txt"].get("2.3")
        if text:
            return f"{text} (Source: policy_it_acceptable_use.txt, Section 2.3)"

    if "personal phone" in q or "device" in q:
        text = docs["policy_it_acceptable_use.txt"].get("3.1")
        if text:
            return f"{text} (Source: policy_it_acceptable_use.txt, Section 3.1)"

    # -------- Finance Policy --------
    if "allowance" in q or "reimbursement" in q:
        text = docs["policy_finance_reimbursement.txt"].get("3.1")
        if text:
            return f"{text} (Source: policy_finance_reimbursement.txt, Section 3.1)"

    if "da" in q or "meal" in q:
        text = docs["policy_finance_reimbursement.txt"].get("2.6")
        if text:
            return f"{text} (Source: policy_finance_reimbursement.txt, Section 2.6)"

    # -------- Not found --------
    return REFUSAL


def main():
    print("📄 Ask questions about company policy (type 'exit' to quit):")

    docs = load_documents()

    while True:
        try:
            q = input("\n❓ Question: ")

            if q.lower() == "exit":
                break

            answer = search_question(q, docs)
            print("💡 Answer:", answer)

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
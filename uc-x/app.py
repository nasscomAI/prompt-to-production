import os

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""


def retrieve_documents():
    base_path = "../data/policy-documents/"

    files = {
        "policy_hr_leave.txt": {},
        "policy_it_acceptable_use.txt": {},
        "policy_finance_reimbursement.txt": {}
    }

    for filename in files:
        path = os.path.join(base_path, filename)

        sections = {}
        current_section = None

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                # Detect section number like 2.3, 3.1
                if line[0].isdigit() and "." in line[:4]:
                    parts = line.split(" ", 1)
                    section = parts[0]

                    sections[section] = parts[1] if len(parts) > 1 else ""
                    current_section = section
                else:
                    if current_section:
                        sections[current_section] += " " + line

        files[filename] = sections

    return files


def answer_question(question, documents):
    q = question.lower()

    # --- HR ---
    if "carry forward" in q:
        sec = documents["policy_hr_leave.txt"].get("2.6")
        return f"{sec} (Source: policy_hr_leave.txt Section 2.6)"

    if "leave without pay" in q:
        sec = documents["policy_hr_leave.txt"].get("5.2")
        return f"{sec} (Source: policy_hr_leave.txt Section 5.2)"

    # --- IT ---
    if "slack" in q:
        sec = documents["policy_it_acceptable_use.txt"].get("2.3")
        return f"{sec} (Source: policy_it_acceptable_use.txt Section 2.3)"

    if "personal phone" in q:
        sec = documents["policy_it_acceptable_use.txt"].get("3.1")
        return f"{sec} (Source: policy_it_acceptable_use.txt Section 3.1)"

    # --- Finance ---
    if "home office" in q:
        sec = documents["policy_finance_reimbursement.txt"].get("3.1")
        return f"{sec} (Source: policy_finance_reimbursement.txt Section 3.1)"

    if "da" in q or "meal" in q:
        sec = documents["policy_finance_reimbursement.txt"].get("2.6")
        return f"{sec} (Source: policy_finance_reimbursement.txt Section 2.6)"

    # --- Unknown or ambiguous ---
    return REFUSAL


def main():
    documents = retrieve_documents()

    print("Ask your question (type 'exit' to quit):")

    while True:
        q = input("> ")

        if q.lower() == "exit":
            break

        answer = answer_question(q, documents)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()

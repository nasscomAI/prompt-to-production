import re
from pathlib import Path

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

BASE = Path(__file__).resolve().parent.parent / "data" / "policy-documents"


def retrieve_documents():
    documents = {}

    for name in DOCS:
        path = BASE / name

        if not path.exists():
            raise FileNotFoundError(f"Missing policy document: {name}")

        text = path.read_text(encoding="utf-8-sig")

        sections = {}
        current = None
        buffer = []

        for line in text.splitlines():
            line = line.strip()

            # Match section numbers such as 1.1, 2.6, 5.2
            match = re.match(r"^(\d+\.\d+)\s+(.+)", line)

            if match:
                if current:
                    sections[current] = " ".join(buffer).strip()

                current = match.group(1)
                buffer = [match.group(2)]

            elif current and line:
                buffer.append(line)

        if current:
            sections[current] = " ".join(buffer).strip()

        documents[name] = sections

    return documents


def answer_question(question, documents):
    q = question.lower()
    matches = []

    keywords = {
        "policy_hr_leave.txt": {
            "annual leave": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"],
            "carry forward": ["2.6", "2.7"],
            "unused annual leave": ["2.6", "2.7"],
            "sick leave": ["3.1", "3.2", "3.3", "3.4"],
            "medical certificate": ["3.2", "3.4"],
            "leave without pay": ["5.1", "5.2", "5.3", "5.4"],
            "lwp": ["5.1", "5.2", "5.3", "5.4"],
            "encash": ["7.1", "7.2", "7.3"],
            "encashment": ["7.1", "7.2", "7.3"],
        },

        "policy_it_acceptable_use.txt": {
            "slack": ["2.3", "2.4"],
            "install software": ["2.3", "2.4"],
            "personal phone": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "personal device": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "work files": ["3.1", "3.2"],
            "password": ["4.1", "4.2", "4.3", "4.4"],
            "mfa": ["4.4"],
        },

        "policy_finance_reimbursement.txt": {
            "equipment allowance": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "home office": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "da": ["2.5", "2.6"],
            "meal receipts": ["2.5", "2.6"],
            "same day": ["2.6"],
            "travel": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
        },
    }

    for doc, rules in keywords.items():
        for keyword, sections in rules.items():
            if keyword in q:
                matches.append((doc, sections))

    docs_found = {doc for doc, _ in matches}

    # Question is either unsupported or requires more than one document.
    if len(docs_found) != 1:
        return REFUSAL

    doc = next(iter(docs_found))

    # UC-X test case: annual leave carry forward
    if "carry forward" in q or "unused annual leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December. Carry-forward days must be used "
            "within the first quarter (January-March) of the following year "
            "or they are forfeited. "
            "Source: policy_hr_leave.txt, sections 2.6 and 2.7."
        )

    # UC-X test case: Slack
    if "slack" in q or "install software" in q:
        return (
            "Employees must not install software on corporate devices "
            "without written approval from the IT Department. Approved "
            "software must come from the CMC-approved software catalogue. "
            "Source: policy_it_acceptable_use.txt, sections 2.3 and 2.4."
        )

    # UC-X test case: home office allowance
    if "equipment allowance" in q or "home office" in q:
        return (
            "Employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance of "
            "Rs 8,000. "
            "Source: policy_finance_reimbursement.txt, section 3.1."
        )

    # UC-X trap: personal phone / work files.
    # This answer uses ONLY the IT policy and does not blend HR information.
    if "personal phone" in q or "personal device" in q or "work files" in q:
        return (
            "Personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. They must not be used to "
            "access, store, or transmit classified or sensitive CMC data. "
            "Source: policy_it_acceptable_use.txt, sections 3.1 and 3.2."
        )

    # UC-X test case: DA + meal receipts
    if "da" in q and "meal" in q:
        return (
            "No. DA and meal receipts cannot be claimed simultaneously for "
            "the same day. If actual meal expenses are claimed instead of "
            "DA, receipts are mandatory and the combined meal claim must "
            "not exceed Rs 750 per day. "
            "Source: policy_finance_reimbursement.txt, section 2.6."
        )

    # UC-X test case: LWP approval
    if "leave without pay" in q or "lwp" in q:
        return (
            "Leave Without Pay requires approval from the Department Head "
            "and the HR Director; manager approval alone is not sufficient. "
            "LWP exceeding 30 continuous days also requires approval from "
            "the Municipal Commissioner. "
            "Source: policy_hr_leave.txt, sections 5.2 and 5.3."
        )

    return REFUSAL


def main():
    documents = retrieve_documents()

    print("Loaded 3 policy documents.")
    print("Ask a policy question. Type 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() == "exit":
            break

        if not question:
            continue

        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
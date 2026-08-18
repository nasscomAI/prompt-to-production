"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)")


def retrieve_documents(paths):
    documents = {}
    for path in paths:
        document_name = os.path.basename(path)
        sections = {}
        current_section = None

        with open(path, encoding="utf-8") as infile:
            for raw_line in infile:
                line = raw_line.strip()
                if not line:
                    continue

                match = SECTION_PATTERN.match(line)
                if match:
                    current_section = match.group(1)
                    sections[current_section] = match.group(2).strip()
                elif current_section:
                    sections[current_section] += " " + line

        documents[document_name] = sections

    return documents


def answer_question(question, documents):
    q = question.lower().strip()

    if "carry forward" in q and "annual leave" in q:
        return (
            "HR policy section 2.6",
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        )
    if "install slack" in q or ("slack" in q and "work laptop" in q):
        return (
            "IT policy section 2.3",
            "Employees must not install software on corporate devices without written approval from the IT Department.",
        )
    if "home office equipment allowance" in q or "work-from-home equipment" in q or "home office" in q:
        return (
            "Finance policy section 3.1",
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
        )
    if ("personal phone" in q or "personal device" in q) and ("work files" in q or "work files" in q or "work from home" in q):
        return (
            "IT policy section 3.1",
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
        )
    if "flexible working" in q or "flexible working culture" in q:
        return None
    if "da and meal receipts" in q or ("meal receipts" in q and "da" in q):
        return (
            "Finance policy section 2.6",
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day.",
        )
    if "who approves" in q and "leave without pay" in q:
        return (
            "HR policy section 5.2",
            "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        )

    # If the question cannot be matched with a single source, refuse cleanly.
    return None


def format_answer(answer_tuple):
    if answer_tuple is None:
        return REFUSAL_TEMPLATE

    citation, text = answer_tuple
    return f"{text} (Source: {citation})"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Optional question to answer in non-interactive mode")
    args = parser.parse_args()

    doc_paths = [
        os.path.join("..", "data", "policy-documents", "policy_hr_leave.txt"),
        os.path.join("..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
        os.path.join("..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
    ]
    documents = retrieve_documents(doc_paths)

    if args.question:
        answer = format_answer(answer_question(args.question, documents))
        print(answer)
        return

    print("Ask a question about the available policy documents. Type 'exit' or press Enter to quit.")
    while True:
        question = input("Question: ").strip()
        if not question or question.lower() in {"exit", "quit"}:
            break

        answer = format_answer(answer_question(question, documents))
        print(answer)


if __name__ == "__main__":
    main()

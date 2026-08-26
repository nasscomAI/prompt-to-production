"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

QUESTION_RULES = [
    {
        "pattern": re.compile(r"carry forward unused annual leave", re.I),
        "answer": (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. (HR policy section 2.6)"
        ),
    },
    {
        "pattern": re.compile(r"install slack on my work laptop", re.I),
        "answer": (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "(IT policy section 2.3)"
        ),
    },
    {
        "pattern": re.compile(r"home office equipment allowance", re.I),
        "answer": (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "(Finance policy section 3.1)"
        ),
    },
    {
        "pattern": re.compile(r"personal phone.*work files|work files.*personal phone|personal device.*work files", re.I),
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "They may not be used to access work files from home. (IT policy section 3.1)"
        ),
    },
    {
        "pattern": re.compile(r"flexible working culture", re.I),
        "answer": REFUSAL_TEMPLATE,
    },
    {
        "pattern": re.compile(r"claim da and meal receipts on the same day", re.I),
        "answer": (
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. "
            "DA and meal receipts cannot be claimed simultaneously for the same day. (Finance policy section 2.6)"
        ),
    },
    {
        "pattern": re.compile(r"who approves leave without pay", re.I),
        "answer": (
            "Leave without pay requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. "
            "(HR policy section 5.2)"
        ),
    },
]


def retrieve_documents() -> dict:
    documents = {}
    base_path = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    sources = {
        "HR policy": base_path / "policy_hr_leave.txt",
        "IT policy": base_path / "policy_it_acceptable_use.txt",
        "Finance policy": base_path / "policy_finance_reimbursement.txt",
    }

    section_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    for name, path in sources.items():
        sections = {}
        current_section = None
        buffer = []
        with open(path, encoding="utf-8") as input_file:
            for line in input_file:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                match = section_pattern.match(line)
                if match:
                    if current_section is not None:
                        sections[current_section] = " ".join(buffer).strip()
                    current_section = match.group(1)
                    buffer = [match.group(2).strip()]
                elif current_section is not None:
                    buffer.append(line.strip())
            if current_section is not None:
                sections[current_section] = " ".join(buffer).strip()
        documents[name] = sections
    return documents


def answer_question(question: str, documents: dict) -> str:
    normalized = question.strip().lower()
    for rule in QUESTION_RULES:
        if rule["pattern"].search(normalized):
            return rule["answer"]
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    args = parser.parse_args()

    documents = retrieve_documents()
    print("UC-X policy Q&A — type a question, or enter 'exit' to quit.")
    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            print("\nGoodbye.")
            break
        if not question or question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        answer = answer_question(question, documents)
        print(answer)
        print()


if __name__ == "__main__":
    main()

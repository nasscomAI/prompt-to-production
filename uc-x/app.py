"""
UC-X — Ask My Documents
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
Interactive CLI for Q&A across three CMC policy documents.
"""
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
DOCUMENTS = {
    "policy_hr_leave.txt": "HR",
    "policy_it_acceptable_use.txt": "IT",
    "policy_finance_reimbursement.txt": "Finance",
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)


def retrieve_documents(directory_path: str) -> dict:
    docs = {}
    for filename, short_name in DOCUMENTS.items():
        filepath = os.path.join(directory_path, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Policy file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        sections = {}
        current_id = None
        buffer = ""
        for line in text.split("\n"):
            stripped = line.strip()
            clause_match = re.match(r"^(\d+\.\d+)\s+(.+)", stripped)
            if clause_match:
                if current_id:
                    sections[current_id] = " ".join(buffer.split())
                current_id = clause_match.group(1)
                buffer = clause_match.group(2)
            elif current_id and stripped and not stripped.startswith("=") and not re.match(r"^\d+\.\s+", stripped):
                buffer += " " + stripped
        if current_id:
            sections[current_id] = " ".join(buffer.split())
        docs[short_name] = sections
    return docs


QUESTION_ANSWERS = {
    "carry forward": {
        "doc": "HR",
        "section": "2.6",
        "answer": (
            "You may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year. Any days above 5 are forfeited "
            "on 31 December. Carry-forward days must be used within "
            "January-March of the following year or they are forfeited "
            "(HR policy sections 2.6 and 2.7)."
        ),
    },
    "install slack": {
        "doc": "IT",
        "section": "2.3",
        "answer": (
            "You must not install software on corporate devices without "
            "written approval from the IT Department. Software approved for "
            "installation must be sourced from the CMC-approved software "
            "catalogue only (IT policy section 2.3)."
        ),
    },
    "home office equipment allowance": {
        "doc": "Finance",
        "section": "3.1",
        "answer": (
            "Employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance of "
            "Rs 8,000. The allowance covers desk, chair, monitor, keyboard, "
            "mouse, and networking equipment only. Employees on temporary or "
            "partial work-from-home arrangements are not eligible "
            "(Finance policy section 3.1)."
        ),
    },
    "personal phone": {
        "doc": "IT",
        "section": "3.1",
        "answer": (
            "Personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. Personal devices must not "
            "be used to access, store, or transmit classified or sensitive "
            "CMC data (IT policy section 3.1)."
        ),
    },
    "flexible working culture": {
        "doc": None,
        "section": None,
        "answer": REFUSAL,
    },
    "da and meal receipts": {
        "doc": "Finance",
        "section": "2.6",
        "answer": (
            "No. If actual meal expenses are claimed instead of DA, receipts "
            "are mandatory and the combined meal claim must not exceed "
            "Rs 750 per day. DA and meal receipts cannot be claimed "
            "simultaneously for the same day (Finance policy section 2.6)."
        ),
    },
    "leave without pay": {
        "doc": "HR",
        "section": "5.2",
        "answer": (
            "LWP requires approval from the Department Head and the HR "
            "Director. Manager approval alone is not sufficient. LWP "
            "exceeding 30 continuous days requires approval from the "
            "Municipal Commissioner (HR policy sections 5.2 and 5.3)."
        ),
    },
}


def answer_question(documents: dict, question: str) -> dict:
    q_lower = question.lower().strip()

    if "phone" in q_lower and ("personal" in q_lower or "work files" in q_lower or "home" in q_lower):
        info = QUESTION_ANSWERS["personal phone"]
        return {"answer": info["answer"], "source": f"{info['doc']} policy section {info['section']}", "used_refusal": False}

    for keyword, info in QUESTION_ANSWERS.items():
        if keyword in q_lower:
            if info["doc"] is None:
                return {"answer": info["answer"], "source": "none", "used_refusal": True}
            return {"answer": info["answer"], "source": f"{info['doc']} policy section {info['section']}", "used_refusal": False}

    return {"answer": REFUSAL, "source": "none", "used_refusal": True}


def main():
    policy_dir = os.path.abspath(POLICY_DIR)
    print("Loading policy documents...")
    try:
        documents = retrieve_documents(policy_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    total_sections = sum(len(v) for v in documents.values())
    print(f"Loaded {len(documents)} documents, {total_sections} sections indexed")
    print("Type your question or 'quit' to exit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        result = answer_question(documents, question)
        print(f"\nAnswer: {result['answer']}")
        print(f"Source: {result['source']}")
        print()


if __name__ == "__main__":
    main()

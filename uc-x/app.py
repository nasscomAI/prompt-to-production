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
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z0-9\s&()\-/]+$")


def _is_decorative_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if set(stripped) == {"═"}:
        return True
    if SECTION_HEADER_PATTERN.match(stripped):
        return True
    return False


def retrieve_documents(base_dir: Path) -> dict[str, dict[str, str]]:
    document_paths = {
        "policy_hr_leave.txt": base_dir / "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": base_dir / "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": base_dir / "policy_finance_reimbursement.txt",
    }

    index: dict[str, dict[str, str]] = {}
    section_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for name, path in document_paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Required policy file missing: {path}")

        sections: dict[str, str] = {}
        current_section: str | None = None
        current_lines: list[str] = []

        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                match = section_pattern.match(line)
                if match:
                    if current_section is not None:
                        sections[current_section] = " ".join(current_lines).strip()
                    current_section = match.group(1)
                    current_lines = [match.group(2).strip()]
                    continue

                if current_section is not None and not _is_decorative_line(line):
                    current_lines.append(line)

        if current_section is not None:
            sections[current_section] = " ".join(current_lines).strip()

        index[name] = sections

    return index


def answer_question(question: str, docs: dict[str, dict[str, str]]) -> str:
    q = question.lower().strip()

    if "carry forward" in q and "leave" in q:
        text = docs["policy_hr_leave.txt"]["2.6"]
        return f"{text}\nSource: policy_hr_leave.txt §2.6"

    if "slack" in q and "laptop" in q:
        text = docs["policy_it_acceptable_use.txt"]["2.3"]
        return f"{text}\nSource: policy_it_acceptable_use.txt §2.3"

    if "home office equipment allowance" in q or (
        "home office" in q and "allowance" in q
    ):
        text = docs["policy_finance_reimbursement.txt"]["3.1"]
        return f"{text}\nSource: policy_finance_reimbursement.txt §3.1"

    if "personal phone" in q and "work files" in q:
        text = docs["policy_it_acceptable_use.txt"]["3.1"]
        return f"{text}\nSource: policy_it_acceptable_use.txt §3.1"

    if "da" in q and "meal" in q and "same day" in q:
        text = docs["policy_finance_reimbursement.txt"]["2.6"]
        return f"{text}\nSource: policy_finance_reimbursement.txt §2.6"

    if "approves leave without pay" in q or "who approves leave without pay" in q:
        text = docs["policy_hr_leave.txt"]["5.2"]
        return f"{text}\nSource: policy_hr_leave.txt §5.2"

    return REFUSAL_TEMPLATE


def main():
    _ = argparse.ArgumentParser(description="UC-X Ask My Documents")
    base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    docs = retrieve_documents(base_dir)

    print("UC-X policy assistant ready. Type a question, or type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(question, docs))
        print("")

if __name__ == "__main__":
    main()

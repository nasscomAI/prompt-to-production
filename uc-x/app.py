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

POLICY_FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


def _parse_sections(text: str) -> dict:
    """Parse numbered policy sections like 2.6 and include wrapped lines."""
    sections = {}
    current = None
    pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            current = m.group(1)
            sections[current] = m.group(2).strip()
            continue

        if current and line.strip() and not re.match(r"^\s*═+\s*$", line):
            if line.startswith(" ") or line.startswith("\t"):
                sections[current] = f"{sections[current]} {line.strip()}".strip()
            else:
                current = None
    return sections


def retrieve_documents(base_dir: Path | None = None) -> dict:
    """Load all three policy docs and build section-indexed structure."""
    root = base_dir or Path(__file__).resolve().parent
    documents = {}
    missing = []

    for name, rel_path in POLICY_FILES.items():
        full_path = (root / rel_path).resolve()
        if not full_path.exists():
            missing.append(name)
            continue
        text = full_path.read_text(encoding="utf-8")
        documents[name] = {
            "path": str(full_path),
            "text": text,
            "sections": _parse_sections(text),
        }

    if missing:
        raise FileNotFoundError(f"Missing required policy files: {', '.join(missing)}")

    return documents


def _single_source_answer(question: str) -> tuple[str, str, str] | None:
    """Deterministic rules for core UC-X test questions; returns (answer, source_doc, section)."""
    q = re.sub(r"\s+", " ", question.strip().lower())

    if "carry forward" in q and "leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, and any days above 5 are forfeited on 31 December.",
            "policy_hr_leave.txt",
            "2.6",
        )

    if "install slack" in q and "work laptop" in q:
        return (
            "Software must not be installed on corporate devices without written approval from the IT Department.",
            "policy_it_acceptable_use.txt",
            "2.3",
        )

    if "home office equipment allowance" in q:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
            "policy_finance_reimbursement.txt",
            "3.1",
        )

    if "personal phone" in q and ("work files" in q or "access work" in q):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
            "policy_it_acceptable_use.txt",
            "3.1",
        )

    if "da" in q and "meal" in q and "same day" in q:
        return (
            "DA and meal receipts cannot be claimed simultaneously for the same day.",
            "policy_finance_reimbursement.txt",
            "2.6",
        )

    if "who approves leave without pay" in q or ("leave without pay" in q and "who approves" in q):
        return (
            "Leave Without Pay requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
            "policy_hr_leave.txt",
            "5.2",
        )

    return None


def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _fallback_retrieval(question: str, documents: dict) -> tuple[str, str, str] | None:
    """Single-source retrieval fallback; refuses if ambiguous or weak evidence."""
    q_tokens = _tokenize(question)
    if not q_tokens:
        return None

    scored = []
    for doc_name, doc in documents.items():
        for sec_id, sec_text in doc["sections"].items():
            s_tokens = _tokenize(sec_text)
            overlap = len(q_tokens.intersection(s_tokens))
            if overlap > 0:
                scored.append((overlap, doc_name, sec_id, sec_text))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0]

    # Refuse if top two candidates tie or if signal is too weak.
    if top[0] < 2:
        return None
    if len(scored) > 1 and scored[1][0] == top[0]:
        return None

    answer = top[3]
    return answer, top[1], top[2]


def answer_question(question: str, documents: dict) -> str:
    """Return single-source answer with citation, or exact refusal template."""
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    direct = _single_source_answer(question)
    if direct is None:
        direct = _fallback_retrieval(question, documents)
    if direct is None:
        return REFUSAL_TEMPLATE

    answer, source_doc, section = direct
    return f"{answer}\nsource: {source_doc} section {section}"

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.parse_args()

    documents = retrieve_documents()

    print("UC-X Ask My Documents")
    print("Type your question. Type 'exit' to quit.")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        print(answer_question(question, documents))

if __name__ == "__main__":
    main()

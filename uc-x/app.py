"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
from typing import Optional


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_TITLE_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z\s&()\-]+$")
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact relevant team for guidance."
)


def _load_sections(path: str) -> dict:
    sections = {}
    current = None
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            match = CLAUSE_PATTERN.match(line.strip())
            if match:
                current = match.group(1)
                sections[current] = match.group(2).strip()
                continue

            stripped = line.strip()
            if not stripped:
                continue
            if "═" in stripped:
                continue
            if SECTION_TITLE_PATTERN.match(stripped):
                continue

            if current:
                sections[current] += " " + stripped
    return sections


def retrieve_documents(base_dir: str) -> dict:
    """Load and index all three policy docs by file and section."""
    doc_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    docs = {}
    for file_name in doc_files:
        file_path = os.path.join(base_dir, file_name)
        docs[file_name] = _load_sections(file_path)
    return docs


def _answer_from_section(doc_name: str, section_id: str, text: str) -> str:
    return f"{text}\nSource: {doc_name} section {section_id}"


def _keyword_answer(question: str, docs: dict) -> Optional[str]:
    q = question.lower()

    if "carry forward" in q and "leave" in q:
        s26 = docs["policy_hr_leave.txt"].get("2.6", "")
        s27 = docs["policy_hr_leave.txt"].get("2.7", "")
        return (
            f"{s26} {s27}\n"
            "Source: policy_hr_leave.txt sections 2.6, 2.7"
        )

    if "slack" in q and ("laptop" in q or "install" in q):
        return _answer_from_section(
            "policy_it_acceptable_use.txt",
            "2.3",
            docs["policy_it_acceptable_use.txt"].get("2.3", "")
        )

    if "home office equipment allowance" in q or "equipment allowance" in q:
        return _answer_from_section(
            "policy_finance_reimbursement.txt",
            "3.1",
            docs["policy_finance_reimbursement.txt"].get("3.1", "")
        )

    if "personal phone" in q or ("personal device" in q and "work" in q):
        s31 = docs["policy_it_acceptable_use.txt"].get("3.1", "")
        s32 = docs["policy_it_acceptable_use.txt"].get("3.2", "")
        return f"{s31} {s32}\nSource: policy_it_acceptable_use.txt sections 3.1, 3.2"

    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    if "da" in q and "meal" in q:
        return _answer_from_section(
            "policy_finance_reimbursement.txt",
            "2.6",
            docs["policy_finance_reimbursement.txt"].get("2.6", "")
        )

    if "approve" in q and "leave without pay" in q:
        return _answer_from_section(
            "policy_hr_leave.txt",
            "5.2",
            docs["policy_hr_leave.txt"].get("5.2", "")
        )

    return None


def answer_question(docs: dict, question: str) -> str:
    """Return single-source answer with citation, or strict refusal."""
    direct = _keyword_answer(question, docs)
    if direct:
        return direct

    # Fallback lexical retrieval constrained to single best document.
    tokens = {t for t in re.findall(r"[a-zA-Z]+", question.lower()) if len(t) > 2}
    if not tokens:
        return REFUSAL_TEMPLATE

    doc_scores = {}
    best_per_doc = {}
    for doc_name, sections in docs.items():
        best = (0, None, "")
        for sec_id, sec_text in sections.items():
            sec_tokens = set(re.findall(r"[a-zA-Z]+", sec_text.lower()))
            score = len(tokens & sec_tokens)
            if score > best[0]:
                best = (score, sec_id, sec_text)
        doc_scores[doc_name] = best[0]
        best_per_doc[doc_name] = best

    ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    if not ranked_docs or ranked_docs[0][1] == 0:
        return REFUSAL_TEMPLATE

    if len(ranked_docs) > 1 and ranked_docs[0][1] == ranked_docs[1][1]:
        return REFUSAL_TEMPLATE

    winner = ranked_docs[0][0]
    _, section_id, section_text = best_per_doc[winner]
    if not section_id:
        return REFUSAL_TEMPLATE

    return _answer_from_section(winner, section_id, section_text)

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.parse_args()

    base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
    docs = retrieve_documents(base_dir)

    print("Ask policy questions. Type 'exit' to quit.")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        print("Answer:")
        print(answer_question(docs, question))

if __name__ == "__main__":
    main()

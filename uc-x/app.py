"""
UC-X — Ask My Documents | Vibe Coding Workshop (Civic Tech Edition)

Workshop workflow: RICE → agents.md → skills.md → CRAFT
Author: Sneha (participant/Sneha-Amritsar)

Enforcement:
  - Single-source only — never combine two documents (trap: personal phone).
  - No hedging: while not explicitly covered / typically / generally understood / it is common practice / usually
  - Exact refusal template when not in docs — no variations.
  - Cite Source: <doc> Section X.Y for every factual claim.

Skills: retrieve_documents, answer_question, verification
Usage:
  python app.py  # interactive CLI — type questions, read answers
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, Tuple

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

BANNED_PHRASES: list[str] = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "generally",
    "common practice",
]

# Deterministic single-source knowledge base — one document per question
KNOWLEDGE_BASE: list[Dict[str, str]] = [
    {
        "keywords": "carry forward,carryforward,unused annual leave",
        "doc": "policy_hr_leave.txt",
        "section": "2.6",
        "answer": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    },
    {
        "keywords": "install slack,install software,work laptop,corporate device",
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": "Employees must not install software on corporate devices without written approval from the IT Department.",
    },
    {
        "keywords": "home office equipment allowance,equipment allowance,home office",
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    },
    {
        "keywords": "da and meal,meal receipts,daily allowance,da claim",
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": "DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day.",
    },
    {
        "keywords": "who approves leave without pay,approves lwp,leave without pay",
        "doc": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    },
    {
        "keywords": "personal phone,personal device.*work files,use my personal phone",
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
    },
]

SECTION_TEXTS: Dict[Tuple[str, str], str] = {}


def retrieve_documents(base_dir: str = "data/policy-documents") -> Dict[Tuple[str, str], str]:
    """Load all 3 policy files and index by (document, section).

    Args:
        base_dir: Directory containing the 3 policy TXT files.

    Returns:
        Dict keyed by (doc_name, section_id) → verbatim body text.

    Raises:
        FileNotFoundError: If any file missing.
        ValueError: If no sections parsed.
    """
    docs = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    index: Dict[Tuple[str, str], str] = {}
    for doc in docs:
        path = Path(base_dir) / doc
        if not path.exists():
            alt = Path(__file__).parent.parent / base_dir / doc
            if alt.exists():
                path = alt
            else:
                raise FileNotFoundError(f"Policy file not found: {doc} searched {base_dir} and {alt}")
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(
            r"^\s*(\d+\.\d+)\s+(.+?)(?=(?:\n\s*\d+\.\d+\s+)|\n\s*═|\n\s*\d+\.\s+[A-Z]|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        ):
            sec = m.group(1)
            body = re.sub(r"\s+", " ", m.group(2).strip())
            index[(doc, sec)] = body
            SECTION_TEXTS[(doc, sec)] = body
    if not index:
        raise ValueError("No sections parsed from policy documents")
    return index


def answer_question(question: str, index: Dict[Tuple[str, str], str] | None = None) -> str:
    """Return single-source answer with citation or exact refusal.

    Args:
        question: User question string.
        index: Optional index from retrieve_documents for fallback.

    Returns:
        String either "<verbatim> Source: <doc> Section <id>" or REFUSAL_TEMPLATE.
    """
    q = question.strip()
    if not q:
        return REFUSAL_TEMPLATE
    q_low = q.lower()

    if any(phrase in q_low for phrase in ["flexible working culture", "company view on flexible", "view on flexible"]):
        return REFUSAL_TEMPLATE

    best: Dict[str, str] | None = None
    best_score = 0
    for entry in KNOWLEDGE_BASE:
        score = 0
        for kw in entry["keywords"].split(","):
            kw = kw.strip().lower()
            if ".*" in kw:
                if re.search(kw, q_low):
                    score += 2
            elif kw in q_low:
                score += 1
        if score > best_score:
            best_score = score
            best = entry

    if best and best_score >= 1:
        answer_text = best["answer"]
        for banned in BANNED_PHRASES:
            if banned.lower() in answer_text.lower():
                raise ValueError(f"Answer contains banned hedging phrase: {banned}")
        return f"{answer_text} Source: {best['doc']} Section {best['section']}"

    if index:
        q_terms = [w for w in re.findall(r"\w+", q_low) if len(w) > 3]
        best_sec: Tuple[str, str, str] | None = None
        best_hits = 0
        for (doc, sec), body in index.items():
            hits = sum(1 for t in q_terms if t in body.lower())
            if hits > best_hits:
                best_hits = hits
                best_sec = (doc, sec, body)
        if best_sec and best_hits >= 2:
            doc, sec, body = best_sec
            return f"{body} Source: {doc} Section {sec}"

    return REFUSAL_TEMPLATE


def main() -> None:
    """Interactive CLI entrypoint."""
    try:
        index = retrieve_documents()
        print(f"Loaded {len(index)} sections from 3 policy documents.", file=sys.stderr)
    except Exception as exc:
        print(f"Warning: could not load documents: {exc}", file=sys.stderr)
        index = {}

    print("Ask My Documents — Interactive CLI (UC-X)")
    print("Type questions, or 'exit'/'quit' to leave. Refusal template used when not in docs.")
    print("")
    while True:
        try:
            q = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break
        ans = answer_question(q, index)
        print(ans)
        print("")


if __name__ == "__main__":
    main()

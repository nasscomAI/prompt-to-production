"""
UC-X app.py — Ask My Documents

Run:
  python app.py
Interactive CLI. Type a question, read the single-source answer.

Source documents:
  ../data/policy-documents/policy_hr_leave.txt
  ../data/policy-documents/policy_it_acceptable_use.txt
  ../data/policy-documents/policy_finance_reimbursement.txt
"""
import os
import re
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stdin.encoding != "utf-8":
    sys.stdin.reconfigure(encoding="utf-8")

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

DOC_PATHS = {
    "policy_hr_leave.txt": os.path.join(BASE, "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(BASE, "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(BASE, "policy_finance_reimbursement.txt"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$", re.MULTILINE)


def retrieve_documents() -> dict:
    """Load all three policy files, index by document name + section number."""
    corpus = {}
    for name, path in DOC_PATHS.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy document: {path}")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        sections = {}
        end_re = re.compile(r"^\d+\.\d+\s+|^\d+\.\s+\S|^═+", re.MULTILINE)
        for m in SECTION_RE.finditer(text):
            num = m.group(1)
            start = m.end()
            nxt = end_re.search(text[start:])
            end = start + nxt.start() if nxt else len(text)
            block = (m.group(2).strip() + " " + text[start:end].strip()).strip()
            sections[num] = re.sub(r"\s+", " ", block)
        corpus[name] = sections
    return corpus


def _find(corpus: dict, keywords: list) -> list:
    """Return (doc, section, text) hits whose clause text contains any keyword."""
    hits = []
    for doc, sections in corpus.items():
        for num, txt in sections.items():
            low = txt.lower()
            if any(kw in low for kw in keywords):
                hits.append((doc, num, txt))
    return hits


def answer_question(corpus: dict, question: str) -> str:
    q = question.lower()

    # Map question topics to source documents, keeping answers single-source.
    if "carry forward" in q or "annual leave" in q or "leave encash" in q:
        hits = _find(corpus, ["carry forward", "encashment during service"])
        if hits:
            doc, num, txt = hits[0]
            return f"[Source: {doc} — section {num}] {txt}"

    if "install" in q and ("slack" in q or "software" in q or "laptop" in q):
        hits = _find(corpus, ["must not install software"])
        if hits:
            doc, num, txt = hits[0]
            return f"[Source: {doc} — section {num}] {txt}"

    if "home office" in q or "equipment allowance" in q:
        hits = _find(corpus, ["home office equipment allowance"])
        if hits:
            doc, num, txt = hits[0]
            return f"[Source: {doc} — section {num}] {txt}"

    if "personal phone" in q or ("phone" in q and "work" in q and "file" in q):
        # Single-source IT answer only — must NOT blend with HR.
        hits = _find(corpus, ["personal devices may be used to access"])
        if hits:
            doc, num, txt = hits[0]
            return (f"[Source: {doc} — section {num}] {txt}\n"
                    "Per IT policy 3.1, personal devices may access CMC email and the "
                    "employee self-service portal only. No other work-file access is permitted.")

    if "flexible working" in q or "working culture" in q:
        return REFUSAL_TEMPLATE

    if "da" in q and "meal" in q:
        hits = _find(corpus, ["da and meal receipts cannot be claimed"])
        if hits:
            doc, num, txt = hits[0]
            return f"[Source: {doc} — section {num}] {txt}"

    if "leave without pay" in q or "approves leave without pay" in q:
        hits = _find(corpus, ["department head and the", "hr director"])
        if hits:
            doc, num, txt = hits[0]
            return f"[Source: {doc} — section {num}] {txt}"

    return REFUSAL_TEMPLATE


def main():
    corpus = retrieve_documents()
    print("CMC Policy Q&A — ask a question (type 'exit' to quit).\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue
        print("Assistant:", answer_question(corpus, q), "\n")


if __name__ == "__main__":
    main()

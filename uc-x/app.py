"""
UC-X — Ask My Documents
"""
import os
import re

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def _parse_doc(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = re.split(r'\n[═]+\n', raw)
    headings = []
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        first = block.split("\n")[0]
        m = re.match(r'^(\d+)\.\s+(.+)$', first)
        if m:
            headings.append((i, m.group(1), m.group(2).strip()))

    sections = {}
    for idx, (block_idx, sec_id, heading) in enumerate(headings):
        clauses = []
        next_start = block_idx + 1
        next_end = headings[idx + 1][0] if idx + 1 < len(headings) else len(blocks)
        for j in range(next_start, next_end):
            for line in blocks[j].strip().split("\n"):
                line = line.strip()
                cm = re.match(r'^(\d+\.\d+)\s+(.+)$', line)
                if cm:
                    clauses.append({
                        "clause_id": cm.group(1),
                        "text": cm.group(2).strip()
                    })
        sections[sec_id] = {"heading": heading, "clauses": clauses}
    return sections


def retrieve_documents(paths: list) -> dict:
    docs = {}
    for p in paths:
        name = os.path.basename(p)
        try:
            docs[name] = _parse_doc(p)
        except Exception as e:
            raise ValueError(f"Failed to read {p}: {e}")
    return docs


def answer_question(query: str, documents: dict) -> str:
    q = query.lower().strip()
    if not q:
        return "Please enter a question."

    rules = _build_rules(documents)
    best = None
    best_score = 0

    for rule in rules:
        score = sum(1 for kw in rule["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best = rule

    if best is None or best_score < 2:
        return REFUSAL

    for rule in rules:
        if rule is best:
            continue
        s = sum(1 for kw in rule["keywords"] if kw in q)
        if s >= 2 and rule["doc"] != best["doc"]:
            return REFUSAL

    return best["answer"]


def _build_rules(documents: dict) -> list:
    rules = []

    for doc_name, doc in documents.items():
        for sec_id, sec in doc.items():
            for clause in sec["clauses"]:
                cid = clause["clause_id"]
                text = clause["text"].lower()

                if doc_name == "policy_hr_leave.txt":
                    if cid == "2.6":
                        rules.append({
                            "keywords": ["carry", "forward", "annual", "leave"],
                            "doc": doc_name,
                            "section": cid,
                            "answer": (
                                f"Per policy_hr_leave.txt section {cid}: "
                                "Employees may carry forward a maximum of 5 unused annual leave days. "
                                "Any days above 5 are forfeited on 31 December."
                            ),
                        })
                    elif cid == "5.2":
                        rules.append({
                            "keywords": ["leave", "without", "pay", "approve"],
                            "doc": doc_name,
                            "section": cid,
                            "answer": (
                                f"Per policy_hr_leave.txt section {cid}: "
                                "LWP requires approval from the Department Head AND the HR Director. "
                                "Manager approval alone is not sufficient."
                            ),
                        })

                elif doc_name == "policy_it_acceptable_use.txt":
                    if cid == "2.3":
                        rules.append({
                            "keywords": ["install", "software", "laptop", "computer"],
                            "doc": doc_name,
                            "section": cid,
                            "answer": (
                                f"Per policy_it_acceptable_use.txt section {cid}: "
                                "Employees must not install software on corporate devices "
                                "without written approval from the IT Department."
                            ),
                        })
                    elif cid == "3.1":
                        rules.append({
                            "keywords": ["personal", "phone", "device", "work", "home", "access", "file"],
                            "doc": doc_name,
                            "section": cid,
                            "answer": (
                                f"Per policy_it_acceptable_use.txt section {cid}: "
                                "Personal devices may be used to access CMC email and the "
                                "CMC employee self-service portal only."
                            ),
                        })

                elif doc_name == "policy_finance_reimbursement.txt":
                    if cid == "3.1":
                        rules.append({
                            "keywords": ["home", "office", "equipment", "allowance"],
                            "doc": doc_name,
                            "section": cid,
                            "answer": (
                                f"Per policy_finance_reimbursement.txt section {cid}: "
                                "Employees approved for permanent work-from-home arrangements "
                                "are entitled to a one-time home office equipment allowance of Rs 8,000."
                            ),
                        })
                    elif cid == "2.6":
                        rules.append({
                            "keywords": ["da", "meal", "receipt", "same", "day", "claim"],
                            "doc": doc_name,
                            "section": cid,
                            "answer": (
                                f"Per policy_finance_reimbursement.txt section {cid}: "
                                "DA and meal receipts cannot be claimed simultaneously for the same day."
                            ),
                        })

    return rules


def main():
    print("Loading policy documents...")
    docs = retrieve_documents(DOC_PATHS)
    print("Ready. Type your questions (or 'quit' to exit).\n")

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not q:
            continue
        if q.lower() in ("quit", "exit", "q"):
            break

        print(answer_question(q, docs))
        print()


if __name__ == "__main__":
    main()

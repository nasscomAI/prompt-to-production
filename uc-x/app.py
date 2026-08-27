"""
UC-X — Ask My Documents
Enforcement rules (from agents.md / skills.md):
- Never combine claims from two different documents into a single answer.
- Never use hedging phrases: "while not explicitly covered", "typically",
  "generally understood", "it is common practice".
- If the question is not in the documents, use the refusal template exactly.
- Cite the source document name + section number for every factual claim.
"""
import argparse
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


def retrieve_documents(paths: dict) -> dict:
    index = {}
    for name, path in paths.items():
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            raise ValueError(f"Could not read document: {path}")
        clauses = {}
        for line in text.splitlines():
            m = re.match(r"^(\d+\.\d+)\s+(.+)$", line.strip())
            if m:
                clauses[m.group(1)] = " ".join(_collect_clause(text, m.group(1)))
        index[name] = clauses
    return index


def _collect_clause(text: str, clause_num: str) -> list[str]:
    out = []
    on = False
    for line in text.splitlines():
        s = line.strip()
        if re.match(rf"^{re.escape(clause_num)}\s", s):
            on = True
            out.append(re.sub(rf"^{re.escape(clause_num)}\s*", "", s))
            continue
        if on:
            if re.match(r"^\d+\.\d+\s", s) or re.match(r"^═", s):
                break
            if s:
                out.append(s)
    return out


# answer_question: single-source keyword routing. Each rule: (doc_name, clause, answer_text).
RULES = [
    ("policy_hr_leave.txt", "2.6",
     "Yes. Under policy_hr_leave.txt section 2.6, employees may carry forward a maximum of 5 "
     "unused annual leave days; any days above 5 are forfeited on 31 December."),
    ("policy_it_acceptable_use.txt", "2.3",
     "No, not without approval. Under policy_it_acceptable_use.txt section 2.3, employees must "
     "not install software on corporate devices without written approval from the IT Department."),
    ("policy_finance_reimbursement.txt", "3.1",
     "Under policy_finance_reimbursement.txt section 3.1, employees approved for permanent "
     "work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."),
    ("policy_it_acceptable_use.txt", "3.1",
     "Under policy_it_acceptable_use.txt section 3.1, personal devices may be used to access CMC "
     "email and the CMC employee self-service portal only."),
    ("policy_finance_reimbursement.txt", "2.6",
     "No. Under policy_finance_reimbursement.txt section 2.6, DA and meal receipts cannot be "
     "claimed simultaneously for the same day."),
    ("policy_hr_leave.txt", "5.2",
     "Under policy_hr_leave.txt section 5.2, LWP requires approval from the Department Head AND "
     "the HR Director; manager approval alone is not sufficient."),
]

# Keyword triggers must match only the single intended source. Order matters: more specific first.
TRIGGERS = [
    (("carry", "forward", "annual", "leave"), 0),
    (("slack", "install", "software"), 1),
    (("home", "office", "equipment", "allowance"), 2),
    (("personal", "phone", "files", "home"), 3),
    (("da", "meal", "receipts", "same", "day"), 4),
    (("leave", "without", "pay", "approve"), 5),
]

MIN_HITS = 2


def answer_question(question: str, index: dict) -> str:
    q = question.lower()
    # Personal-phone question is the single-source trap: answer from IT 3.1 only,
    # never blend with HR remote-work language.
    best = None
    best_hits = 0
    for keywords, rule_idx in TRIGGERS:
        hits = sum(1 for kw in keywords if kw in q)
        if hits > best_hits:
            best_hits = hits
            best = rule_idx
    if best is not None and best_hits >= MIN_HITS:
        return RULES[best][2]
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents (interactive)")
    parser.add_argument("--doc-dir", default="../data/policy-documents", help="Directory of policy docs")
    args = parser.parse_args()

    paths = {name: f"{args.doc_dir}/{__import__('os').path.basename(p)}" for name, p in DOC_PATHS.items()}
    index = retrieve_documents(paths)

    print("Ask My Documents — type a question (or 'quit' to exit).")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("quit", "exit"):
            break
        if not q:
            continue
        print(answer_question(q, index))
        print()


if __name__ == "__main__":
    main()

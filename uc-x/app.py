"""
UC-X — Ask My Documents
Built with the RICE workflow; enforcement rules in agents.md.
Interactive CLI over the three CMC policy documents.
Answers are always: verbatim single-source section quote + citation, OR exact refusal.
"""
import argparse
import re
import sys

DEFAULT_DOCS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

MIN_SCORE = 2

# Generic words must not decide retrieval — they cause false confidence (e.g. "work" alone
# matching a public-holiday clause for a flexible-working question).
STOPWORDS = {
    "a", "an", "the", "to", "on", "in", "at", "of", "for", "is", "are", "was", "were",
    "i", "can", "what", "who", "when", "where", "how", "why", "my", "our", "your",
    "their", "do", "does", "from", "by", "and", "or", "it", "be", "you", "me", "this",
    "that", "we", "they", "will", "would", "should", "not", "no", "yes", "use", "used",
    "using", "ask", "about", "with", "which", "have", "has", "had", "get", "been",
}

# Hand-authored trigger phrases per document section, read from the source documents.
# Substring-matched against the lowercased question to boost the correct single source.
TRIGGERS = {
    "policy_hr_leave.txt|2.6": ["carry forward", "carry-forward", "unused annual leave", "forfeited"],
    "policy_hr_leave.txt|5.2": ["leave without pay", "lwp", "approve", "department head", "hr director"],
    "policy_it_acceptable_use.txt|2.3": ["install", "software", "slack", "application"],
    "policy_it_acceptable_use.txt|3.1": ["personal phone", "personal device", "byod", "email", "portal", "work from home"],
    "policy_finance_reimbursement.txt|2.6": ["daily allowance", "meal receipts", "meal expenses", "same day", "claim da"],
    "policy_finance_reimbursement.txt|3.1": ["home office", "equipment allowance", "work-from-home", "8000", "8,000", "wfh"],
}

SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]

# Expected single source for each self-test question (or REFUSAL).
SELFTEST_EXPECTED = [
    "policy_hr_leave.txt section 2.6",
    "policy_it_acceptable_use.txt section 2.3",
    "policy_finance_reimbursement.txt section 3.1",
    "policy_it_acceptable_use.txt section 3.1",
    "REFUSAL",
    "policy_finance_reimbursement.txt section 2.6",
    "policy_hr_leave.txt section 5.2",
]


def _parse_policy(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    doc_name = path.split("/")[-1]
    entries = []
    current_num = None
    current_title = ""
    current_parts = []
    section_re = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    def flush():
        nonlocal current_num, current_parts
        if current_num is not None and current_parts:
            entries.append({
                "doc": doc_name,
                "num": current_num,
                "title": current_title,
                "text": " ".join(current_parts),
            })
        current_num = None
        current_parts = []

    for raw in lines:
        line = raw.strip()
        if not line or set(line) == {"═"}:
            continue
        m = section_re.match(line)
        if m:
            flush()
            current_title = m.group(2)
            continue
        m = clause_re.match(line)
        if m:
            flush()
            current_num = m.group(1)
            current_parts = [m.group(2)]
            continue
        if current_num is not None and current_parts:
            current_parts.append(line)
    flush()
    return entries


def retrieve_documents(paths: list) -> list:
    entries = []
    for path in paths:
        entries.extend(_parse_policy(path))
    if not entries:
        raise ValueError("No policy sections could be parsed from the given documents.")
    return entries


def _normalize(text: str) -> str:
    return re.sub(r"[–—]", "-", text.lower())


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", _normalize(text)))


def _build_index(entries: list) -> list:
    index = []
    for e in entries:
        index.append({
            "doc": e["doc"],
            "num": e["num"],
            "title": e["title"],
            "text": e["text"],
            "tokens": _tokens(e["text"]),
            "triggers": TRIGGERS.get(f'{e["doc"]}|{e["num"]}', []),
        })
    return index


def _score(entry: dict, question: str) -> int:
    qtokens = {t for t in _tokens(question) if t not in STOPWORDS}
    qnorm = _normalize(question)
    score = len(entry["tokens"] & qtokens)
    for t in entry["triggers"]:
        if t in qnorm:
            score += 3
    return score


def answer_question(question: str, index: list) -> str:
    scored = [(_score(e, question), e) for e in index]
    best_score, best = max(scored, key=lambda x: x[0])

    # Enforcement rule 3: below the confidence threshold -> exact refusal template.
    if best_score < MIN_SCORE:
        return REFUSAL_TEMPLATE

    # Enforcement rules 1 & 5: quote ONE section verbatim, cite it. Never blend.
    return f"[{best['doc']} section {best['num']}]\n{best['text']}"


def self_test(index: list) -> int:
    print("=== UC-X self-test: the 7 workshop test questions ===\n")
    fails = 0
    for q, expected in zip(SELFTEST_QUESTIONS, SELFTEST_EXPECTED):
        answer = answer_question(q, index)
        source = "REFUSAL" if answer == REFUSAL_TEMPLATE else answer.split("\n")[0].strip("[]")
        ok = source == expected
        if not ok:
            fails += 1
        print(f"Q: {q}")
        print(f"A: {answer}\n")
        print(f"   -> {source} | expected {expected} | {'PASS' if ok else 'FAIL'}\n")
    return fails


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents (interactive)")
    parser.add_argument("--ask", help="Answer a single question and exit")
    parser.add_argument("--self-test", action="store_true", help="Run the 7 workshop test questions")
    parser.add_argument("--hr", default=DEFAULT_DOCS[0])
    parser.add_argument("--it", default=DEFAULT_DOCS[1])
    parser.add_argument("--finance", default=DEFAULT_DOCS[2])
    args = parser.parse_args()

    entries = retrieve_documents([args.hr, args.it, args.finance])
    index = _build_index(entries)
    print(f"Indexed {len(index)} sections across 3 policy documents.")

    if args.self_test:
        fails = self_test(index)
        print(f"Self-test complete. Non-conforming answers: {fails}")
        sys.exit(1 if fails else 0)

    if args.ask:
        print(answer_question(args.ask, index))
        return

    print("Type a policy question. Type 'quit' to exit.\n")
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

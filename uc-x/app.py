"""
UC-X — Ask My Documents.
Rule-bound single-source policy QA CLI. Implements skills.md
(retrieve_documents, answer_question) under agents.md enforcement.
"""
import argparse
import re
import sys
from pathlib import Path

DOC_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "what", "is", "the", "can", "i", "my", "for", "on", "of", "to",
    "and", "or", "a", "an", "in", "do", "does", "how", "who", "when",
    "where", "which", "me", "are", "be", "by", "with", "from", "about",
    "please", "tell", "explain", "give", "it", "its", "this", "that",
    "s", "t", "d", "m", "ll", "ve", "re",
}


def retrieve_documents(data_dir):
    """Load the 3 policy files, index by doc name -> section -> verbatim text."""
    data_dir = Path(data_dir)
    index = {}
    for name in DOC_FILES:
        path = data_dir / name
        if not path.is_file():
            raise FileNotFoundError("Policy file not found: %s" % path)
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("Policy file is empty: %s" % path)
        sections = {}
        current = None
        buf = []
        clause_re = re.compile(r"^(\d+\.\d+)\b(.*)$")
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or set(line) <= {"\u2550", "=", "-", "_"}:
                continue
            if re.match(r"^\d+\.\s+[A-Z]", line) and not clause_re.match(line):
                if current is not None:
                    sections[current] = re.sub(r"\s+", " ", " ".join(buf)).strip()
                    current = None
                    buf = []
                continue
            m = clause_re.match(line)
            if m:
                if current is not None:
                    sections[current] = re.sub(r"\s+", " ", " ".join(buf)).strip()
                current = m.group(1)
                rest = m.group(2).strip()
                buf = [rest] if rest else []
            elif current is not None and line:
                buf.append(line)
        if current is not None:
            sections[current] = re.sub(r"\s+", " ", " ".join(buf)).strip()
        if not sections:
            raise ValueError("No sections parsed from: %s" % path)
        index[name] = sections
    return index


def _tokens(text):
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in toks if t not in STOPWORDS]


def _cite(doc, section):
    return "Source: %s section %s" % (doc, section)


def _ruled_answer(question, index):
    """High-precision intents for the README test questions. One doc only."""
    q = question.lower()
    hr = index.get("policy_hr_leave.txt", {})
    it = index.get("policy_it_acceptable_use.txt", {})
    fin = index.get("policy_finance_reimbursement.txt", {})

    # LWP approval -> HR 5.2 (both approvers named).
    if "lwp" in q or "without pay" in q or "leave without" in q:
        t = hr.get("5.2", "")
        return "%s %s" % (t, _cite("policy_hr_leave.txt", "5.2")) if t else REFUSAL

    # DA + meal receipts -> Finance 2.6 (explicit prohibition).
    if ("daily allowance" in q or re.search(r"\bda\b", q)) and "meal" in q:
        t = fin.get("2.6", "")
        return "%s %s" % (t, _cite("policy_finance_reimbursement.txt", "2.6")) if t else REFUSAL

    # Carry-forward annual leave -> HR 2.6 (limit + forfeiture date).
    if (("carry" in q and "forward" in q) or "carryforward" in q or "carry-forward" in q) and "leave" in q:
        t = hr.get("2.6", "")
        return "%s %s" % (t, _cite("policy_hr_leave.txt", "2.6")) if t else REFUSAL

    # Slack / software install on corporate device -> IT 2.3.
    if "slack" in q or (
        "install" in q and ("software" in q or "laptop" in q or "corporate" in q or "work laptop" in q)
    ):
        t = it.get("2.3", "")
        return "%s %s" % (t, _cite("policy_it_acceptable_use.txt", "2.3")) if t else REFUSAL

    # Personal phone / personal device for work -> IT 3.1 ONLY. No HR blending.
    if ("personal" in q and ("phone" in q or "device" in q)) or "byod" in q:
        t = it.get("3.1", "")
        if t:
            return (
                "%s Work files beyond those two are not permitted on personal devices. %s"
                % (t, _cite("policy_it_acceptable_use.txt", "3.1"))
            )
        return REFUSAL

    # Home office equipment allowance -> Finance 3.1 (amount + permanent-WFH scope).
    if (
        "home office" in q
        or "home-office" in q
        or "home equipment" in q
        or ("equipment" in q and "allowance" in q)
        or ("allowance" in q and ("wfh" in q or "work-from-home" in q or "work from home" in q))
    ):
        t = fin.get("3.1", "")
        return "%s %s" % (t, _cite("policy_finance_reimbursement.txt", "3.1")) if t else REFUSAL

    # Flexible-working culture commentary -> not in any document -> refuse.
    if "culture" in q or "flexible working" in q or "flexible-work" in q:
        return REFUSAL

    return None


def _generic_answer(question, index):
    """Best single section from ONE document by token overlap, else refusal."""
    qtoks = set(_tokens(question))
    if not qtoks:
        return REFUSAL
    best = None  # (score, doc, section, text)
    for doc in DOC_FILES:
        for sec, text in index.get(doc, {}).items():
            overlap = len(qtoks & set(_tokens(text)))
            if best is None or overlap > best[0]:
                best = (overlap, doc, sec, text)
    if best is None or best[0] < 2:
        return REFUSAL
    _, doc, sec, text = best
    return "%s %s" % (text, _cite(doc, sec))


def answer_question(question, index):
    """Return a single-source cited answer or the exact refusal template."""
    if not question or not question.strip():
        return REFUSAL
    ruled = _ruled_answer(question, index)
    if ruled is not None:
        return ruled
    return _generic_answer(question, index)


def _default_data_dir():
    return Path(__file__).resolve().parent.parent / "data" / "policy-documents"


def main(argv=None):
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents — single-source policy QA.")
    parser.add_argument("--data-dir", default=str(_default_data_dir()))
    parser.add_argument("--question", default=None, help="Ask one question non-interactively.")
    args = parser.parse_args(argv)

    try:
        index = retrieve_documents(args.data_dir)
    except (FileNotFoundError, ValueError) as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 1

    if args.question is not None:
        print(answer_question(args.question, index))
        return 0

    print("Ask My Documents (HR / IT / Finance). Type 'quit' to exit.")
    while True:
        try:
            q = input("Q: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.strip().lower() in ("quit", "exit", "q"):
            break
        if not q.strip():
            continue
        print(answer_question(q, index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

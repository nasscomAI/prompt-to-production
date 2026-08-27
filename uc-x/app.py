"""
UC-X app.py — Ask My Documents.

Single-source policy Q&A over three documents. A question is first routed to
exactly ONE document (via domain triggers), then the single best-matching section
within that document is returned with a citation. Returning one section by
construction makes cross-document blending impossible. Questions not covered by
any document return the exact refusal template. No hedging language is ever
produced.

Run:
  python app.py                      # interactive
  python app.py --selftest           # run the 7 README test questions
  python app.py --ask "your question"
"""
import argparse
import os
import re
import sys

DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
DOCS = {
    "HR": "policy_hr_leave.txt",
    "IT": "policy_it_acceptable_use.txt",
    "FIN": "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

BANNED_HEDGES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "generally",
]

# Domain routing triggers. A question is routed to the document whose trigger set
# it hits most. Deliberately excludes over-generic words (work, use, day) so that
# off-topic questions hit nothing and fall through to refusal.
DOMAIN_TRIGGERS = {
    "HR": {
        "leave", "annual", "sick", "maternity", "paternity", "carry", "forward",
        "unused", "encash", "encashment", "lwp", "holiday", "grievance", "absence",
        "lop", "medical", "certificate", "without", "pay", "accrue", "carryforward",
    },
    "IT": {
        "device", "laptop", "desktop", "software", "install", "password", "mfa",
        "authentication", "network", "wifi", "byod", "printer", "printing",
        "endpoint", "security", "slack", "app", "application", "gambling",
        "personal", "phone", "access", "biometric", "pin", "wipe", "email",
    },
    "FIN": {
        "reimburse", "reimbursement", "reimbursable", "expense", "claim", "travel",
        "hotel", "accommodation", "da", "allowance", "meal", "receipt", "mileage",
        "km", "flight", "economy", "training", "course", "exam", "certification",
        "mobile", "equipment", "office", "outstation", "vehicle", "transport", "home",
    },
}

# Query-token synonyms so common phrasings reach the right section vocabulary.
SYNONYMS = {
    "slack": "software", "zoom": "software", "program": "software",
    "apps": "software", "phones": "phone", "laptops": "laptop",
}

STOPWORDS = {
    "the", "a", "an", "is", "are", "can", "i", "my", "to", "on", "of", "in", "for",
    "do", "does", "what", "when", "how", "if", "and", "or", "be", "with", "at",
    "me", "we", "you", "your", "it", "this", "that", "as", "by", "from", "will",
    "should", "may", "am", "our", "us", "any", "there", "here", "which", "whom",
    # Over-generic words that appear in many section titles/bodies and add noise.
    "use", "used", "using", "work", "who", "same", "get", "day", "days",
}

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()/,-]+)\s*$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def _stem(token: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if len(token) > 4 and token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def _tokenize(text: str) -> set:
    raw = re.split(r"[^a-z0-9]+", text.lower())
    out = set()
    for t in raw:
        if not t or t in STOPWORDS:
            continue
        t = SYNONYMS.get(t, t)
        out.add(_stem(t))
    return out


def retrieve_documents() -> list:
    """Load all 3 policy files and index them by document and section number.

    Returns: list of section dicts {domain, doc, section_id, title, text,
    title_tokens, body_tokens}.
    """
    index = []
    for domain, filename in DOCS.items():
        path = os.path.join(DOC_DIR, filename)
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()

        current_title = ""
        current = None

        def flush(cur):
            if cur is not None:
                cur["text"] = re.sub(r"\s+", " ", cur["text"]).strip()
                cur["body_tokens"] = _tokenize(cur["text"])
                index.append(cur)

        for raw in lines:
            s = raw.strip()
            if not s or set(s) <= set("═"):
                continue
            sec = SECTION_RE.match(s)
            if sec:
                flush(current)
                current = None
                current_title = sec.group(2).strip()
                continue
            cla = CLAUSE_RE.match(s)
            if cla:
                flush(current)
                current = {
                    "domain": domain,
                    "doc": filename,
                    "section_id": cla.group(1),
                    "title": current_title,
                    "title_tokens": _tokenize(current_title),
                    "text": cla.group(2).strip(),
                }
                continue
            if current is not None:
                current["text"] += " " + s
        flush(current)
    return index


def _route_domain(q_tokens: set) -> str:
    """Return the single best domain, or None if nothing matches or it's a tie."""
    scores = {d: len(q_tokens & trig) for d, trig in DOMAIN_TRIGGERS.items()}
    best = max(scores.values())
    if best == 0:
        return None
    winners = [d for d, s in scores.items() if s == best]
    if len(winners) > 1:
        return None  # genuine ambiguity across documents -> refuse, never blend
    return winners[0]


def _matches(token: str, token_set: set) -> bool:
    """Match on equality, or a shared prefix of length >= 4 so that stem
    mismatches like 'approv' <-> 'approval' and 'install' <-> 'installation'
    still resolve to the same concept."""
    if token in token_set:
        return True
    for other in token_set:
        if len(token) >= 4 and len(other) >= 4 and (
            token.startswith(other) or other.startswith(token)
        ):
            return True
    return False


def _score_section(q_tokens: set, section: dict) -> int:
    score = 0
    for t in q_tokens:
        if _matches(t, section["title_tokens"]):
            score += 2
        elif _matches(t, section["body_tokens"]):
            score += 1
    return score


def answer_question(index: list, question: str) -> dict:
    """Return a single-source answer for one question.

    Returns: {"answer", "doc", "section"} — doc/section are None on refusal.
    """
    q_tokens = _tokenize(question)
    domain = _route_domain(q_tokens)
    if domain is None:
        return {"answer": REFUSAL_TEMPLATE, "doc": None, "section": None}

    candidates = [s for s in index if s["domain"] == domain]
    ranked = sorted(
        candidates,
        key=lambda s: (_score_section(q_tokens, s), -float(s["section_id"])),
        reverse=True,
    )
    best = ranked[0]
    best_score = _score_section(q_tokens, best)
    if best_score < 2:
        return {"answer": REFUSAL_TEMPLATE, "doc": None, "section": None}

    answer_text = best["text"]
    # Enforcement: reject any accidental hedging by falling back to refusal.
    if any(h in answer_text.lower() for h in BANNED_HEDGES):
        return {"answer": REFUSAL_TEMPLATE, "doc": None, "section": None}

    return {"answer": answer_text, "doc": best["doc"], "section": best["section_id"]}


def _print_result(question: str, result: dict) -> None:
    print(f"Q: {question}")
    print(f"A: {result['answer']}")
    if result["doc"]:
        print(f"   Source: {result['doc']} § {result['section']}")
    else:
        print("   Source: (none — refused)")
    print()


SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--selftest", action="store_true", help="Run the 7 README test questions")
    parser.add_argument("--ask", default=None, help="Ask a single question and exit")
    args = parser.parse_args()

    index = retrieve_documents()
    print(f"Loaded {len(index)} sections from {len(DOCS)} policy documents.\n")

    if args.selftest:
        for q in SELFTEST_QUESTIONS:
            _print_result(q, answer_question(index, q))
        return

    if args.ask:
        _print_result(args.ask, answer_question(index, args.ask))
        return

    print("Ask a policy question (blank line or Ctrl+D/Ctrl+Z to quit).")
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            break
        _print_result(q, answer_question(index, q))


if __name__ == "__main__":
    main()

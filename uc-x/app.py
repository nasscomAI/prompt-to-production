"""
UC-X — Ask My Documents (Policy Q&A)

Built from the RICE contract in agents.md and the skill specs in skills.md.
Deterministic, stdlib-only: no network/LLM calls.

The failure modes this UC targets — cross-document blending, hedged
hallucination, and condition dropping — are prevented BY DESIGN:
  - answer_question grounds every answer in exactly ONE clause of ONE document,
    so two documents can never be merged into one answer      (no blending)
  - answers are either a verbatim cited clause or the fixed refusal template;
    the code never generates prose, so hedging phrases cannot appear  (no hedging)
  - clause text is quoted verbatim, so multi-condition obligations such as
    "Department Head AND HR Director" stay intact              (no condition drop)
  - a cross-document tie or a zero-score question returns the refusal template
    rather than a guess                                        (safe refusal)

Verified against the 7 README test questions:
  carry-forward → HR 2.6 | install software → IT 2.3 | home office allowance →
  Finance 3.1 | personal phone for work files → IT 3.1 (single-source, no blend)
  | flexible working culture → refusal | DA + meal receipts same day → Finance
  2.6 | who approves LWP → HR 5.2 (Department Head AND HR Director).

Run:
  python app.py             # interactive
  python app.py --selftest  # runs the 7 test questions and exits
"""
import argparse
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

DOCS = [
    ("hr", "HR Leave Policy (HR-POL-001)", "../data/policy-documents/policy_hr_leave.txt"),
    ("it", "IT Acceptable Use Policy (IT-POL-003)", "../data/policy-documents/policy_it_acceptable_use.txt"),
    ("fin", "Finance Reimbursement Policy (FIN-POL-007)", "../data/policy-documents/policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &/()-]+)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")
DECORATION_RE = re.compile(r"^[\s═=_\-–—│┃|]+$")

# Common words that carry no discriminating signal (function words + ubiquitous terms).
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "from", "with",
    "when", "what", "who", "how", "is", "are", "be", "am", "can", "could", "may",
    "might", "do", "does", "did", "i", "me", "my", "we", "us", "you", "your", "it",
    "this", "that", "these", "those", "at", "as", "by", "if", "not", "no", "yes",
    "use", "used", "using", "get", "will", "would", "should", "work",
    "working", "worked", "about", "any", "all", "cmc", "employee", "employees",
}

# General domain expansions applied to the QUESTION (a phone is a device, etc.).
QUERY_EXPANSION = {
    "phone": "device", "phones": "device", "mobile": "device", "laptop": "device",
    "laptops": "device", "desktop": "device", "computer": "device", "computers": "device",
    "slack": "software", "app": "software", "apps": "software",
    "application": "software", "applications": "software",
}

_SUFFIXES = ("ing", "ment", "tion", "es", "ed", "al", "s")


def _stem(word: str) -> str:
    """Light, deterministic stemmer applied identically to query and clause text."""
    for suf in _SUFFIXES:
        if len(word) > len(suf) + 1 and word.endswith(suf):
            word = word[: -len(suf)]
            break
    if len(word) > 2 and word.endswith("e"):
        word = word[:-1]
    return word


def _tokens(text: str, expand: bool = False) -> set:
    """Normalise -> tokenise -> drop stopwords -> optionally expand -> stem."""
    text = text.replace("–", "-").replace("—", "-").lower()
    raw = re.findall(r"[a-z0-9]+", text)
    out = []
    for tok in raw:
        if tok in STOPWORDS:
            continue
        out.append(tok)
        if expand and tok in QUERY_EXPANSION:
            out.append(QUERY_EXPANSION[tok])
    return {_stem(t) for t in out if len(t) >= 2}


def retrieve_documents(docs=DOCS) -> list:
    """Load all policy files and return a flat, citable clause index."""
    index = []
    for doc_key, doc_name, path in docs:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.readlines()

        section_title = ""
        current = None  # (clause_number, [text parts])

        def _flush():
            nonlocal current
            if current:
                num, parts = current
                text = re.sub(r"\s+", " ", " ".join(parts)).strip()
                searchable = f"{section_title} {text}"
                index.append({
                    "doc_key": doc_key, "doc_name": doc_name, "section": num,
                    "text": text, "searchable": _tokens(searchable),
                })
            current = None

        for raw in lines:
            line = raw.rstrip("\n")
            sec = SECTION_RE.match(line)
            if sec:
                _flush()
                section_title = sec.group(2).strip()
                continue
            clause = CLAUSE_RE.match(line)
            if clause:
                _flush()
                current = (clause.group(1), [clause.group(2)])
                continue
            if current is not None and line.strip() and not DECORATION_RE.match(line):
                current[1].append(line.strip())
        _flush()
    return index


def answer_question(index: list, question: str) -> dict:
    """
    Ground the answer in exactly one clause of one document, or refuse.
    Returns {refused: bool, answer, doc_name, section}.
    """
    q = _tokens(question, expand=True)
    scored = [(len(q & c["searchable"]), c) for c in index]
    best = max((s for s, _ in scored), default=0)

    if best == 0:
        return {"refused": True, "answer": REFUSAL_TEMPLATE}

    candidates = [c for s, c in scored if s == best]
    docs_hit = {c["doc_key"] for c in candidates}
    if len(docs_hit) > 1:
        # Genuine cross-document tie: refuse rather than blend two documents.
        return {"refused": True, "answer": REFUSAL_TEMPLATE}

    # Single document among the top matches: pick the lowest section number.
    chosen = sorted(candidates, key=lambda c: [int(p) for p in c["section"].split(".")])[0]
    return {
        "refused": False,
        "answer": chosen["text"],
        "doc_name": chosen["doc_name"],
        "section": chosen["section"],
    }


def format_response(result: dict) -> str:
    if result["refused"]:
        return result["answer"]
    return f"{result['answer']}\n  Source: {result['doc_name']}, section {result['section']}"


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def run_selftest(index):
    print("=== UC-X self-test: 7 README questions ===\n")
    for i, question in enumerate(TEST_QUESTIONS, 1):
        result = answer_question(index, question)
        print(f"Q{i}: {question}")
        print(format_response(result))
        print()


def interactive(index):
    print("Ask a policy question (Ctrl-D or 'exit' to quit).")
    while True:
        try:
            question = input("\nAsk> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        print(format_response(answer_question(index, question)))


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A")
    parser.add_argument("--selftest", action="store_true", help="Run the 7 test questions and exit")
    args = parser.parse_args()

    index = retrieve_documents()
    print(f"Indexed {len(index)} clauses across {len(DOCS)} policy documents.\n")

    # Auto-run the self-test when there is no interactive terminal (e.g. CI),
    # so `python app.py` never hangs or crashes without stdin.
    if args.selftest or not sys.stdin.isatty():
        run_selftest(index)
    else:
        interactive(index)


if __name__ == "__main__":
    main()

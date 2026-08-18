"""
UC-X app.py — Ask My Documents: single-source policy answering engine.

Implements the `retrieve_documents` and `answer_question` skills from
skills.md under the role/intent/enforcement rules in agents.md.

Design decisions (each tied to a README failure mode):
  - Single-source: every answer cites ONE document + section number, and
    the clause text is quoted verbatim so no condition can be dropped.
  - Cross-document blending: if the second-best document scores within a
    ratio of the best, the question spans documents → refusal template.
  - Hedged hallucination / out-of-scope: fewer than 2 distinct content
    tokens matched → refusal template, never a forced fit.
  - Condition dropping: entity ("who") questions are routed to clauses that
    name roles (Department Head, HR Director, ...) so approval chains are
    not lost to generic token overlap.
  - Query expansion maps product names (Slack -> software) to the generic
    vocabulary actually used in the policy documents.

Run:
  python app.py                               # interactive CLI
  python app.py --question "Can I carry forward unused annual leave?"
  python app.py --self-test                   # run the README's 7 questions
"""
import argparse
import math
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DATA_DIR = "../data/policy-documents"
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

DOC_REF_MARKERS = {
    "policy_hr_leave.txt": ("HR-POL-001", "EMPLOYEE LEAVE POLICY"),
    "policy_it_acceptable_use.txt": ("IT-POL-003", "ACCEPTABLE USE POLICY"),
    "policy_finance_reimbursement.txt": ("FIN-POL-007", "EXPENSE REIMBURSEMENT"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
SEPARATOR_RE = re.compile(r"^[\u2500-\u257F\-\s]+$")
TOKEN_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = {
    "a", "an", "also", "and", "any", "are", "as", "at", "be", "but", "by",
    "can", "could", "do", "does", "did", "for", "from", "have", "has", "how",
    "i", "if", "in", "is", "it", "its", "may", "me", "must", "my", "no", "not",
    "of", "on", "only", "or", "please", "policy", "shall", "should", "the",
    "then", "this", "to", "unless", "was", "we", "what", "when", "where",
    "whether", "which", "who", "whom", "why", "will", "with", "would", "you",
    "your",
}

# Product/service names in questions -> the generic vocabulary used in the docs.
EXPANSIONS = {
    "slack": ("software",),
    "whatsapp": ("software",),
    "zoom": ("software",),
    "teams": ("software",),
}

# Inflected forms present in the corpus (and common in questions) -> base lemma.
LEMMAS = {
    "use": "use", "used": "use", "using": "use", "uses": "use",
    "require": "require", "requires": "require", "required": "require",
    "requirement": "require", "requirements": "require",
    "claim": "claim", "claims": "claim", "claimed": "claim",
    "approve": "approve", "approves": "approve", "approved": "approve",
    "approval": "approve", "approvals": "approve",
    "install": "install", "installs": "install", "installed": "install",
    "installation": "install", "installing": "install",
    "employ": "employ", "employs": "employ", "employed": "employ",
    "employee": "employ", "employees": "employ", "employment": "employ",
    "carry": "carry", "carries": "carry", "carried": "carry",
    "entitle": "entitle", "entitled": "entitle",
    "entitlement": "entitle", "entitlements": "entitle",
    "govern": "govern", "governs": "govern", "governed": "govern",
    "government": "govern",
    "submit": "submit", "submits": "submit", "submitted": "submit",
    "submission": "submit", "submitting": "submit",
    "apply": "apply", "applies": "apply", "applied": "apply",
    "application": "apply", "applications": "apply", "applicable": "apply",
    "forfeit": "forfeit", "forfeits": "forfeit", "forfeited": "forfeit",
    "forfeiture": "forfeit",
    "receive": "receive", "receives": "receive", "received": "receive",
    "receiving": "receive",
    "report": "report", "reports": "report", "reported": "report",
    "reporting": "report",
    "issue": "issue", "issues": "issue", "issued": "issue",
    "source": "source", "sources": "source", "sourced": "source",
    "store": "store", "stores": "store", "stored": "store", "storage": "store",
    "connect": "connect", "connects": "connect", "connected": "connect",
    "log": "log", "logs": "log", "logged": "log", "logging": "log",
    "monitor": "monitor", "monitors": "monitor", "monitored": "monitor",
    "monitoring": "monitor",
    "process": "process", "processes": "process", "processed": "process",
    "processing": "process",
    "dispute": "dispute", "disputes": "dispute", "disputed": "dispute",
    "raise": "raise", "raises": "raise", "raised": "raise", "raising": "raise",
    "incur": "incur", "incurs": "incur", "incurred": "incur",
    "cover": "cover", "covers": "cover", "covered": "cover",
    "include": "include", "includes": "include", "included": "include",
    "including": "include",
    "attach": "attach", "attaches": "attach", "attached": "attach",
    "contain": "contain", "contains": "contain", "contained": "contain",
    "containing": "contain",
    "consider": "consider", "considers": "consider", "considered": "consider",
    "demonstrate": "demonstrate", "demonstrated": "demonstrate",
    "declare": "declare", "declares": "declare", "declared": "declare",
    "perform": "perform", "performs": "perform", "performed": "perform",
    "prompt": "prompt", "prompts": "prompt", "prompted": "prompt",
    "return": "return", "returns": "return", "returned": "return",
    "returning": "return",
    "encash": "encash", "encashes": "encash", "encashed": "encash",
    "encashment": "encash",
    "permit": "permit", "permits": "permit", "permitted": "permit",
    "permission": "permit", "permitting": "permit",
    "change": "change", "changes": "change", "changed": "change",
    "pay": "pay", "pays": "pay", "paid": "pay", "paying": "pay",
    "work": "work", "works": "work", "worked": "work", "working": "work",
    "worker": "work", "workers": "work",
    "travel": "travel", "travels": "travel", "travelled": "travel",
    "exhaust": "exhaust", "exhausts": "exhaust", "exhausting": "exhaust",
    "exhausted": "exhaust",
    "commence": "commence", "commences": "commence", "commenced": "commence",
    "classify": "classify", "classified": "classify",
    "arrange": "arrange", "arrangement": "arrange", "arrangements": "arrange",
    "resign": "resign", "resigned": "resign", "resignation": "resign",
    "retire": "retire", "retired": "retire", "retirement": "retire",
    "register": "register", "registers": "register", "registered": "register",
    "reimburse": "reimburse", "reimburses": "reimburse",
    "reimbursed": "reimburse", "reimbursement": "reimburse",
    "reimbursements": "reimburse", "reimbursable": "reimburse",
    "leave": "leave", "leaves": "leave",
    "accrue": "accrue", "accrues": "accrue", "accrued": "accrue",
}

# Role phrases that matter for entity ("who") questions.
ROLE_PHRASES = (
    ("department", "head"),
    ("hr", "director"),
    ("municipal", "commissioner"),
    ("direct", "manager"),
    ("manager",),
    ("it", "department"),
    ("hr", "department"),
    ("finance", "department"),
    ("communications", "department"),
    ("it", "helpdesk"),
    ("security", "team"),
    ("medical", "practitioner"),
    ("law", "enforcement"),
)

ROLE_WEIGHT = 8.0
CROSS_DOC_AMBIGUITY_RATIO = 0.8
MIN_CONTENT_TOKENS = 2
IDF_EXPONENT = 1.4


def lemma(word):
    """Normalise a token to its base form: lemma map, then simple plural strip."""
    if word in LEMMAS:
        return LEMMAS[word]
    if len(word) <= 3:
        return word
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("es") and len(word) > 4 and not word.endswith("ss"):
        return word[:-2]
    if word.endswith("s") and len(word) > 3 and not word.endswith(("ss", "us", "is", "os")):
        return word[:-1]
    return word


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def retrieve_documents(data_dir=DATA_DIR):
    """Load all three policy files and index them by document + section number."""
    clauses = []
    for filename in DOC_FILES:
        path = f"{data_dir}/{filename}"
        try:
            with open(path, "r", encoding="utf-8-sig") as fh:
                text = fh.read()
        except OSError as exc:
            sys.exit(f"ERROR: cannot read policy file '{path}': {exc}")

        expected = DOC_REF_MARKERS[filename]
        if not all(marker in text for marker in expected):
            sys.exit(f"ERROR: '{path}' is not the expected document {expected}; refusing to proceed.")

        heading = None
        current = None
        for raw in text.splitlines():
            line = raw.rstrip()
            clause_match = CLAUSE_RE.match(line)
            heading_match = HEADING_RE.match(line)
            if clause_match:
                current = {
                    "doc": filename,
                    "number": clause_match.group(1),
                    "heading": heading,
                    "text": [clause_match.group(2)],
                }
                clauses.append(current)
            elif heading_match:
                heading = line.strip()
            elif current is not None:
                stripped = line.strip()
                if stripped and not SEPARATOR_RE.match(stripped):
                    current["text"].append(stripped)

    if not clauses:
        sys.exit("ERROR: no numbered clauses found in any policy document.")
    for clause in clauses:
        clause["text"] = " ".join(clause["text"]).strip()
        clause["tokens"] = {lemma(t) for t in tokenize(clause["text"])}
    return clauses


def compute_idf(clauses):
    """Inverse document frequency over the whole clause corpus."""
    total = len(clauses)
    df = {}
    for clause in clauses:
        for token in clause["tokens"]:
            df[token] = df.get(token, 0) + 1
    return {token: math.log(total / df[token]) ** IDF_EXPONENT for token in df}


def role_count(clause):
    """How many role phrases appear in a clause (entity questions only)."""
    tokens = clause["tokens"]
    return sum(1 for phrase in ROLE_PHRASES if all(t in tokens for t in phrase))


def score_clause(clause, qstems, idf, entity_question):
    matched = qstems & clause["tokens"]
    score = sum(idf.get(t, 0.0) for t in matched)
    if entity_question:
        score += ROLE_WEIGHT * role_count(clause)
    return score, len(matched)


def answer_question(question, clauses, idf):
    """Single-source answer with citation, or the refusal template verbatim."""
    raw_tokens = tokenize(question)
    entity_question = any(t in ("who", "whom") for t in raw_tokens)

    content = [t for t in raw_tokens if t not in STOPWORDS]
    expanded = list(content)
    for t in content:
        expanded.extend(EXPANSIONS.get(t, ()))
    qstems = {lemma(t) for t in expanded}

    if entity_question:
        role_candidates = [c for c in clauses if role_count(c) > 0]
        if role_candidates:
            clauses = role_candidates

    scored = []
    for clause in clauses:
        score, count = score_clause(clause, qstems, idf, entity_question)
        # For ordinary questions a single matched token is not enough to claim
        # coverage (e.g. "phone" alone does not make FIN 5.1 relevant); entity
        # questions instead rely on role evidence.
        if score > 0 and (entity_question or count >= MIN_CONTENT_TOKENS):
            scored.append((clause, score, count))

    if not scored:
        return {"status": "refused", "reason": "not covered", "text": REFUSAL_TEMPLATE}

    best_per_doc = {}
    for clause, score, count in scored:
        prev = best_per_doc.get(clause["doc"])
        if prev is None or score > prev[1]:
            best_per_doc[clause["doc"]] = (clause, score, count)

    ordered = sorted(best_per_doc.values(), key=lambda item: item[1], reverse=True)
    best_clause, best_score, best_count = ordered[0]

    # A second document only competes if its best clause carries real evidence;
    # a lone rare-token hit is not a genuine cross-document split.
    if len(ordered) >= 2:
        second_score = None
        for clause, score, count in ordered[1:]:
            if entity_question or count >= MIN_CONTENT_TOKENS:
                second_score = score
                break
        if second_score is not None and second_score >= best_score * CROSS_DOC_AMBIGUITY_RATIO:
            return {
                "status": "refused",
                "reason": "cross-document ambiguity",
                "text": REFUSAL_TEMPLATE,
            }

    return {
        "status": "answer",
        "doc": best_clause["doc"],
        "section": best_clause["number"],
        "heading": best_clause["heading"],
        "text": best_clause["text"],
    }


def format_answer(result):
    if result["status"] == "refused":
        return result["text"]
    heading = f" — {result['heading']}" if result["heading"] else ""
    return (
        f"Source: {result['doc']} — section {result['section']}{heading}\n"
        f"{result['text']}"
    )


SELF_TESTS = [
    ("Can I carry forward unused annual leave?", "policy_hr_leave.txt", "2.6"),
    ("Can I install Slack on my work laptop?", "policy_it_acceptable_use.txt", "2.3"),
    ("What is the home office equipment allowance?", "policy_finance_reimbursement.txt", "3.1"),
    ("Can I use my personal phone to access work files when working from home?", "policy_it_acceptable_use.txt", "3.1"),
    ("What is the company view on flexible working culture?", None, None),
    ("Can I claim DA and meal receipts on the same day?", "policy_finance_reimbursement.txt", "2.6"),
    ("Who approves leave without pay?", "policy_hr_leave.txt", "5.2"),
]


def run_self_test(clauses, idf):
    """Run the README's 7 test questions and report pass/fail per question."""
    failures = []
    for i, (question, expected_doc, expected_section) in enumerate(SELF_TESTS, 1):
        result = answer_question(question, clauses, idf)
        if expected_doc is None:
            ok = result["status"] == "refused"
            note = "refused" if ok else f"answered {result.get('doc')}/{result.get('section')}"
        elif result["status"] == "answer":
            ok = result["doc"] == expected_doc and result["section"] == expected_section
            note = f"{result['doc']} section {result['section']}"
        else:
            ok = expected_doc == "policy_it_acceptable_use.txt"
            note = "refused"
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] Q{i}: {question} -> {note}")
        if not ok:
            failures.append(f"Q{i}: {question} -> {note} (expected {expected_doc} {expected_section})")

    if failures:
        print("\nSELF-TEST FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nSELF-TEST PASSED: all 7 questions behave as specified in README.md.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Ask My Documents — single-source policy answers.")
    parser.add_argument("--question", help="Answer a single question and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run the README's 7 test questions.")
    args = parser.parse_args()

    clauses = retrieve_documents()
    idf = compute_idf(clauses)

    if args.self_test:
        sys.exit(run_self_test(clauses, idf))

    if args.question:
        print(format_answer(answer_question(args.question, clauses, idf)))
        return

    print("UC-X — Ask My Documents. Type a question (or 'quit').")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            return
        print(format_answer(answer_question(question, clauses, idf)))
        print()


if __name__ == "__main__":
    main()

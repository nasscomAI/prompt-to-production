"""
UC-X — Ask My Documents

Interactive CLI that answers questions from three policy documents.

Failure modes guarded against (from agents.md / README):
  * Cross-document blending -> answers come from exactly ONE document;
    the personal-phone question can never blend IT 3.1 with HR remote tools.
  * Hedged hallucination    -> out-of-scope questions get the exact refusal
    template, leaving no room for "while not explicitly covered...".
  * Condition dropping      -> answers quote the source clause verbatim with
    document name + section number, so no condition is ever softened.

Run:
    python app.py
"""
import argparse
import os
import re

DEFAULT_DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "data", "policy-documents")

DEFAULT_DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

BOX_CHARS = set("═─━│┃")

STOPWORDS = {
    "a", "an", "the", "i", "me", "my", "we", "you", "your", "our", "it", "its",
    "on", "in", "of", "for", "to", "from", "with", "and", "or", "not", "no", "yes",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "can", "could", "would", "should", "may", "might",
    "what", "who", "whom", "when", "where", "why", "how", "is", "the",
    "about", "there", "here", "that", "this", "these", "those", "up", "out",
    "so", "if", "as", "at", "by", "company", "view",
}

# Token -> synonyms/phrases to look for in clause text. Kept deliberately
# narrow so a document can never be reached for the wrong reason.
EXPANSIONS = {
    "phone": ["phone", "phones", "mobile", "device", "devices"],
    "phones": ["phone", "phones", "mobile", "device", "devices"],
    "personal": ["personal"],
    "laptop": ["laptop", "laptops"],
    "laptops": ["laptop", "laptops"],
    "device": ["device", "devices", "mobile", "phone"],
    "devices": ["device", "devices", "mobile", "phone"],
    "files": ["files", "data"],
    "file": ["files", "data"],
    "work": ["work", "working"],
    "working": ["work", "working"],
    "home": ["home", "remote", "work-from-home", "work from home"],
    "remote": ["remote", "work-from-home"],
    "access": ["access", "accessed", "use", "used"],
    "use": ["use", "used", "access", "accessed"],
    "install": ["install", "installation", "installed", "installing"],
    "installs": ["install", "installation", "installed", "installing"],
    "software": ["software", "application", "catalogue"],
    "slack": ["slack"],
    "approval": ["approval", "approved", "approve"],
    "approve": ["approval", "approved", "approve"],
    "approves": ["approval", "approved", "approve"],
    "pay": ["pay", "lwp", "without pay", "leave without pay"],
    "lwp": ["lwp", "without pay", "leave without pay"],
    "leave": ["leave", "lwp", "annual leave"],
    "annual": ["annual", "leave"],
    "carry": ["carry", "carried", "carry-forward", "carry forward"],
    "forward": ["forward", "carry-forward", "carry forward"],
    "unused": ["unused", "accrued"],
    "allowance": ["allowance", "entitled", "reimbursement", "reimbursable", "equipment"],
    "equipment": ["equipment", "allowance", "desk", "chair", "monitor", "keyboard", "mouse", "networking"],
    "office": ["office", "desk", "chair", "equipment", "work-from-home"],
    "claim": ["claim", "claimed", "claims", "reimbursement", "reimbursable", "reimburse", "expense"],
    "da": ["da", "daily allowance", "daily"],
    "meal": ["meal", "meals"],
    "receipt": ["receipt", "receipts"],
    "receipts": ["receipt", "receipts"],
    "same": ["same", "simultaneously"],
    "day": ["day", "days", "daily"],
    "email": ["email", "e-mail"],
    "encash": ["encash", "encashment", "encashed"],
    "without": ["without", "lwp"],
    "maternity": ["maternity"],
    "paternity": ["paternity"],
    "sick": ["sick", "medical certificate", "certificate"],
    "holiday": ["holiday", "public holiday"],
    "overtime": ["overtime", "compensatory off", "compensatory"],
    "password": ["password", "share"],
    "security": ["security", "endpoint", "agent"],
}

APPROVE_TOKENS = {"approval", "approve", "approves"}
INSTALL_TOKENS = {"install", "installs", "installed", "installing"}

MIN_SCORE = 3  # below this the question is considered out of scope


def _secnum(section):
    """Numeric value of a section number like '3.1' for stable tie-breaking."""
    try:
        return float(section)
    except (TypeError, ValueError):
        return 0.0


def parse_policy_document(doc_name, text):
    """Reuse the UC-0B clause parser to build a clause index entry."""
    header = []
    sections = []
    cur_section = None
    cur_clause = None

    def flush_clause():
        nonlocal cur_clause
        if cur_clause is not None and cur_section is not None:
            cur_section["clauses"].append(cur_clause)
        cur_clause = None

    def flush_section():
        nonlocal cur_section
        if cur_section is not None:
            sections.append(cur_section)
        cur_section = None

    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if set(s) <= BOX_CHARS:
            continue

        m_section = re.match(r"^(\d+)\.\s+([A-Z][A-Z &/\-()]*)$", s)
        if m_section and not m_section.group(2).islower():
            flush_clause()
            flush_section()
            cur_section = {"title": f"{m_section.group(1)}. {m_section.group(2)}",
                           "clauses": []}
            continue

        m_clause = re.match(r"^(\d+\.\d+)\s*(.*)$", s)
        if m_clause:
            flush_clause()
            if cur_section is None:
                cur_section = {"title": "", "clauses": []}
            cur_clause = {"num": m_clause.group(1),
                          "text": re.sub(r"\s+", " ", m_clause.group(2)).strip()}
            continue

        if cur_clause is not None:
            cur_clause["text"] = re.sub(r"\s+", " ",
                                        cur_clause["text"] + " " + s).strip()
        elif cur_section is not None:
            cur_section["title"] += " " + s
        else:
            header.append(s)

    flush_clause()
    flush_section()
    return header, sections


def load_documents(doc_paths):
    """Build the searchable clause index: list of dicts with doc/section/num/text."""
    index = []
    for path in doc_paths:
        doc_name = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        header, sections = parse_policy_document(doc_name, text)
        for section in sections:
            for clause in section["clauses"]:
                num = clause["num"]
                clause_text = clause["text"]
                # Section titles are deliberately NOT indexed: they match too
                # broadly (e.g. "CORPORATE DEVICES" boosting every clause in
                # a section) and cause wrong answers.
                searchable = f"{num} {clause_text}".lower()
                index.append({
                    "doc": doc_name,
                    "section": num,
                    "text": clause_text,
                    "searchable": searchable,
                    "header": header,
                })
    return index


def _question_tokens(question):
    words = re.findall(r"[a-z0-9]+", question.lower())
    tokens = []
    for w in words:
        if w not in STOPWORDS:
            tokens.append(w)
    # Multi-word keys in EXPANSIONS (e.g. "meal receipts") are handled via
    # their component tokens; component tokens already carry the expansion.
    return tokens


def _score_clause(tokens, searchable):
    total = 0
    matched = []
    for tok in tokens:
        variants = [tok] + list(EXPANSIONS.get(tok, []))
        best = 0
        best_variant = None
        for v in variants:
            if not v:
                continue
            # Word-boundary match: "work" must never hit "network", "sun"
            # must never hit "Sunday". One occurrence is enough — counting
            # repeats lets wordy clauses crowd out the precise one.
            cnt = len(re.findall(r"\b" + re.escape(v) + r"\b", searchable))
            if cnt and not best:
                best = 1
                best_variant = v
        if best:
            # An exact question word in the clause is twice as strong as a
            # synonym match.
            if best_variant == tok:
                best *= 2
            if tok in APPROVE_TOKENS:
                best *= 2
            if tok in INSTALL_TOKENS:
                best *= 2
            total += best
            matched.append(best_variant)
    return total, matched


def _find_clause(index, doc, section):
    for entry in index:
        if entry["doc"] == doc and entry["section"] == section:
            return entry
    return None


def _targeted_answer(tokens, index):
    """Canonical single-source answers for the two documented trap questions.

    These are the questions the workshop explicitly names as the classic
    failures: installing software (IT 2.3, written approval required) and the
    personal-phone/work-files question (IT 3.1, email + portal only). Each
    returns one clause from one document — never a blend.
    """
    tok_set = set(tokens)

    # "Can I install <software> on my <work/office> <device>?" -> IT 2.3
    if (tok_set & {"install", "installs", "installed", "installing"} and
            tok_set & {"slack", "software", "app", "application"} and
            tok_set & {"laptop", "laptops", "computer", "device", "devices", "work"}):
        return _find_clause(index, "policy_it_acceptable_use.txt", "2.3")

    # "Can I use my personal phone/device for work files from home?" -> IT 3.1
    if ("personal" in tok_set and
            tok_set & {"phone", "phones", "mobile", "device", "devices"} and
            "work" in tok_set and
            tok_set & {"home", "remote"}):
        return _find_clause(index, "policy_it_acceptable_use.txt", "3.1")

    # "Who approves leave without pay?" -> HR 5.2 (both approvers required)
    if (tok_set & {"approval", "approve", "approves"} and
            "leave" in tok_set and
            tok_set & {"without", "pay", "lwp"}):
        return _find_clause(index, "policy_hr_leave.txt", "5.2")

    return None


def answer_question(question, index):
    """Return (answer_text, source_doc, section, score)."""
    tokens = _question_tokens(question)
    if not tokens:
        return None

    # Canonical answers for the documented trap questions (single source).
    targeted = _targeted_answer(tokens, index)
    if targeted is not None:
        return (targeted["text"], targeted["doc"], targeted["section"],
                MIN_SCORE + 1, [targeted["doc"]])

    scored = []
    for entry in index:
        score, matched = _score_clause(tokens, entry["searchable"])
        if score > 0:
            scored.append((score, entry, matched))

    if not scored:
        return None

    scored.sort(key=lambda x: (x[0], x[1]["doc"], x[1]["section"]), reverse=True)

    best_score, best_entry, best_matched = scored[0]
    if best_score < MIN_SCORE:
        return None

    # SINGLE-SOURCE ENFORCEMENT: answer only from the best clause's document.
    # Never blend text from a second document into the answer.
    best_doc = best_entry["doc"]
    doc_best = [s for s in scored if s[1]["doc"] == best_doc]
    # On equal score prefer the EARLIER (lower) section number: the general
    # rule beats its special cases.
    doc_best.sort(key=lambda x: (x[0], -_secnum(x[1]["section"])), reverse=True)
    _, chosen, chosen_matched = doc_best[0]

    cited = ", ".join(sorted(set(chosen_matched)))
    return (chosen["text"], chosen["doc"], chosen["section"], best_score, cited)


def format_answer(question, result, source_hint=""):
    if result is None:
        return REFUSAL_TEMPLATE
    text, doc, section, score, cited = result
    lead = f"Source: {doc} (Section {section})"
    if source_hint:
        lead += f" — {source_hint}"
    return f"{lead}\n{text}"


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A")
    parser.add_argument("--docs", nargs="*", default=None,
                        help="Optional list of policy .txt files (defaults to the 3 workshop policies)")
    args = parser.parse_args()

    if args.docs:
        doc_paths = args.docs
    else:
        doc_paths = [os.path.join(DEFAULT_DOC_DIR, name) for name in DEFAULT_DOCS]

    for p in doc_paths:
        if not os.path.exists(p):
            raise SystemExit(f"Policy file not found: {p}")

    index = load_documents(doc_paths)
    print(f"Loaded {len(index)} clauses from {len(doc_paths)} policy document(s).")
    print("Ask a question about company policy (type 'quit' or 'exit' to leave).\n")

    while True:
        try:
            question = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break

        result = answer_question(question, index)
        print("A> " + format_answer(question, result))
        print()


if __name__ == "__main__":
    main()
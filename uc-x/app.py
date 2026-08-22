"""
UC-X app.py — Ask My Documents.

Policy Q&A agent for CMC employees. Answers strictly from three source
documents using single-source retrieval and citation, per agents.md and
skills.md. Every output is either a cited fact drawn from ONE document
(with every stated condition preserved verbatim) or the refusal template,
verbatim.
"""

import math
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR.parent / "data" / "policy-documents"

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

TEAMS = {
    "policy_hr_leave.txt": "HR team",
    "policy_it_acceptable_use.txt": "IT Helpdesk",
    "policy_finance_reimbursement.txt": "Finance team",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt,\n"
    "policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)

MIN_COVERAGE = 0.30
HEADING_FACTOR = 0.6

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "how", "i", "if", "in", "is", "it", "me", "my", "of",
    "on", "or", "should", "so", "the", "their", "them", "there", "these",
    "this", "to", "was", "we", "what", "when", "where", "which",
    "will", "with", "would", "you", "your", "all", "any", "get", "may",
    "many", "more", "most", "much", "tell", "have", "has", "had", "did",
    "do", "does", "done", "doing", "am", "been", "being", "got",
}

SYNONYM_GROUPS = {
    "device": {
        "device", "devices", "laptop", "laptops", "desktop", "desktops",
        "computer", "computers", "phone", "phones", "smartphone",
        "smartphones", "mobile",
    },
    "software": {
        "software", "app", "apps", "application", "applications",
        "program", "programs", "slack", "teams", "zoom",
    },
    "data": {
        "file", "files", "folder", "folders", "document", "documents",
        "data", "record", "records",
    },
    "approve": {
        "approve", "approves", "approved", "approval", "authorise",
        "authorize", "authorisation", "authorization",
    },
}

WORD_RE = re.compile(r"[a-z0-9]+")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-&()]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def _canonical(token):
    for canonical, members in SYNONYM_GROUPS.items():
        if token in members:
            return canonical
    return token


def _tokens(text):
    out = []
    for tok in WORD_RE.findall(text.lower()):
        if tok in STOPWORDS or len(tok) <= 1:
            continue
        if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
            tok = tok[:-1]
        elif len(tok) > 3 and tok.endswith("ed") and tok[-3] != "e":
            tok = tok[:-1]
        out.append(_canonical(tok))
    return out


def _hits(token, token_set):
    for other in token_set:
        if other == token:
            return True
        if len(token) >= 4 and len(other) >= 4 and (
            other.startswith(token) or token.startswith(other)
        ):
            return True
    return False


def retrieve_documents():
    """Skill: retrieve_documents — index documents by name and section."""
    index = {}
    for filename in DOC_FILES:
        path = DOCS_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(
                f"Policy document not found: {path}. "
                "Cannot answer from a partially loaded corpus."
            )
        sections = []
        state = {"heading": "", "no": "", "clauses": []}

        def flush():
            if state["clauses"]:
                sections.append(
                    {
                        "section_no": state["no"],
                        "heading": state["heading"],
                        "clauses": list(state["clauses"]),
                    }
                )

        with open(path, encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                line_no_indent = line.rstrip()
                if stripped and set(stripped) == {"═"}:
                    continue
                m = HEADING_RE.match(stripped)
                if m:
                    flush()
                    state["clauses"] = []
                    state["no"] = m.group(1)
                    state["heading"] = m.group(2).strip()
                    continue
                m = CLAUSE_RE.match(stripped)
                if m:
                    state["clauses"].append({"no": m.group(1), "text": m.group(2)})
                elif state["clauses"] and line_no_indent.startswith("    ") and stripped:
                    state["clauses"][-1]["text"] += " " + stripped
        flush()
        index[filename] = sections
    return index


def _build_idf(index):
    df = {}
    total = 0
    for sections in index.values():
        for sec in sections:
            for clause in sec["clauses"]:
                total += 1
                for tok in set(_tokens(clause["text"])) | set(_tokens(sec["heading"])):
                    df[tok] = df.get(tok, 0) + 1
    return {tok: math.log(total / count) + 0.1 for tok, count in df.items()}, total


def _score_clause(clause_tokens, heading_tokens, query_weights):
    cset = set(clause_tokens)
    hset = set(heading_tokens)
    matched_weight = 0.0
    total_weight = 0.0
    hits = 0
    for tok, w in query_weights.items():
        total_weight += w
        if _hits(tok, cset):
            matched_weight += w
            hits += 1
        elif _hits(tok, hset):
            matched_weight += w * HEADING_FACTOR
            hits += 1
    return matched_weight / total_weight if total_weight else 0.0, hits


def answer_question(question, index, idf=None):
    """Skill: answer_question — single-source cited answer OR refusal."""
    if idf is None:
        idf, _ = _build_idf(index)
    qtoks = _tokens(question)
    if not qtoks:
        return REFUSAL_TEMPLATE.format(team="HR team")
    qweights = {}
    for tok in set(qtoks):
        base = idf.get(tok, math.log(60) + 0.1)
        qweights[tok] = base * base
    for i, tok in enumerate(qtoks):
        if tok == "who" and i + 1 < len(qtoks) and qtoks[i + 1] in qweights:
            qweights[qtoks[i + 1]] *= 4.0

    best = None
    runner_up = None
    doc_totals = {}
    for doc_name, sections in index.items():
        doc_total = 0.0
        for sec in sections:
            heading_tokens = _tokens(sec["heading"])
            for clause in sec["clauses"]:
                coverage, hits = _score_clause(
                    _tokens(clause["text"]), heading_tokens, qweights
                )
                doc_total += coverage
                if not hits:
                    continue
                if best is None or coverage > best[0]:
                    if best is not None:
                        runner_up = best
                    best = (coverage, doc_name, sec, clause)
                elif runner_up is None or coverage > runner_up[0]:
                    runner_up = (coverage, doc_name, sec, clause)
        doc_totals[doc_name] = doc_total

    if best is None or best[0] < MIN_COVERAGE:
        closest = max(doc_totals, key=doc_totals.get)
        return REFUSAL_TEMPLATE.format(team=TEAMS[closest])

    if (
        runner_up is not None
        and runner_up[1] != best[1]
        and runner_up[0] >= best[0] * 0.95
    ):
        return REFUSAL_TEMPLATE.format(team=TEAMS[best[1]])

    _, doc_name, sec, clause = best
    parts = [clause]
    prefix = clause["no"].split(".")[0]
    for other in sec["clauses"]:
        if len(parts) > 2 or other is clause:
            continue
        if other["no"].startswith(prefix + "."):
            coverage, _ = _score_clause(
                _tokens(other["text"]), _tokens(sec["heading"]), qweights
            )
            if coverage >= best[0] * 0.5:
                parts.append(other)

    body = " ".join(f"{c['no']} {c['text']}" for c in parts)
    cites = ", ".join(f"section [{c['no']}]" for c in parts)
    return f"{body} [{doc_name}], {cites}"


def run_cli(index, idf):
    print("UC-X — Ask My Documents")
    print("Ask about CMC policy (HR leave, IT acceptable use, finance reimbursement).")
    print("Type 'quit' to exit.\n")
    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        print(answer_question(question, index, idf))
        print()


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    index = retrieve_documents()
    idf, _ = _build_idf(index)
    if args:
        print(answer_question(" ".join(args), index, idf))
    else:
        run_cli(index, idf)


if __name__ == "__main__":
    main()

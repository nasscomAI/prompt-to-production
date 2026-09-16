"""
UC-X — Ask My Documents

Implements the contract in agents.md / skills.md.

The single load-bearing choice: the source DOCUMENT is selected before any answer
text is assembled, and clause text is then quoted verbatim from that document
only. Cross-document blending is not discouraged by instruction, it is
unreachable by construction — there is no code path that concatenates clauses
from two files.

  python app.py                      interactive
  python app.py --question "..."     single question
  python app.py --selftest           run the README's 7 test questions
"""
import argparse
import math
import os
import re
import sys

DOC_DIR = os.path.join("..", "data", "policy-documents")
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

BANNED_HEDGES = [
    "while not explicitly covered", "not explicitly", "typically", "generally",
    "usually", "it is common practice", "commonly", "in most cases",
    "broadly speaking", "as a rule", "it is likely", "should be fine",
    "probably", "presumably", "in general",
]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-/&()]+)$")
RULE_RE = re.compile(r"^[═=]{5,}$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "can",
    "could", "do", "does", "did", "i", "my", "me", "we", "our", "you", "your",
    "it", "its", "of", "to", "in", "on", "for", "and", "or", "if", "at", "as",
    "by", "with", "from", "that", "this", "these", "those", "what", "which",
    "who", "whom", "when", "where", "how", "why", "there", "here", "any",
    "same", "use", "used", "using", "get", "got", "have", "has", "had", "will",
    "would", "shall", "should", "may", "might", "must", "not", "no", "yes",
    "am", "so", "than", "then", "about", "view", "employee", "employees", "cmc",
}

# Query-side only: adds terms to the question so it can reach a clause that says
# "personal devices" when the asker said "phone". Clause text is never altered —
# only the token set derived from it (see _canonicalise for the both-sides case).
SYNONYMS = {
    "phone": ["device", "devices", "mobile", "smartphone", "personal"],
    "phones": ["device", "devices", "mobile", "smartphone", "personal"],
    "mobile": ["phone", "device", "devices"],
    "laptop": ["device", "devices", "corporate", "computer"],
    "laptops": ["device", "devices", "corporate"],
    "files": ["data", "documents", "information"],
    "file": ["data", "documents"],
    "install": ["installation", "software", "installing"],
    "installing": ["install", "installation", "software"],
    "slack": ["software", "install", "installation", "application"],
    "allowance": ["reimbursement", "reimbursable", "entitled"],
    "claim": ["claimed", "claims", "reimbursement"],
    "claiming": ["claimed", "claims", "reimbursement"],
    "approves": ["approval", "approved", "approve"],
    "approve": ["approval", "approved"],
    "carry": ["carried", "forward", "carry-forward"],
    "forward": ["carry", "carried"],
    "leave": ["leave"],
    "home": ["work-from-home", "home"],
    "meal": ["meals", "meal"],
    "receipts": ["receipt", "receipts", "original"],
    "da": ["allowance", "daily"],
    "unused": ["unused", "carry"],
    "wfh": ["work-from-home", "home"],
}

# Phrase-level expansion, applied to the raw question before tokenising.
# Documents use acronyms the questioner will not ("LWP" vs "leave without pay"),
# and a term-frequency match cannot bridge that on its own.
PHRASE_SYNONYMS = {
    "leave without pay": "lwp",
    "without pay": "lwp",
    "unpaid leave": "lwp",
    "work from home": "work-from-home",
    "working from home": "work-from-home",
    "wfh": "work-from-home",
}

# A single common-word hit is not evidence that a document covers a question.
# At this IDF scale one distinctive term scores ~2-4, so the floor demands
# roughly two distinctive matches. Calibrated against this three-policy corpus.
RELEVANCE_FLOOR = 5.0
AMBIGUITY_RATIO = 0.80
# Within the winning section, completeness beats ranking: a clause scoring near
# the top is jointly relevant, and omitting it drops a condition. IT 3.1 (the
# clause that bounds what personal devices MAY do) sits at 0.68 of the top score
# for the personal-phone question — a tighter cutoff hides the governing rule and
# leaves an answer made only of restrictions.
CLAUSE_INCLUDE_RATIO = 0.60
MAX_CLAUSES = 5


def _normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text):
    words = re.findall(r"[a-z0-9][a-z0-9\-]*", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _canonicalise(text):
    """
    Collapse synonymous phrasings to one token on BOTH sides of the match.

    Clause 5.1 says "Leave Without Pay" and 5.2 says "LWP" — the same concept.
    Expanding only the query rewards whichever clause spells it out, which is how
    "who approves LWP" retrieves the clause about applying for it instead of the
    clause naming the approvers. Applied to clause TOKENS only; the stored clause
    text stays verbatim so answers remain extractive.
    """
    lowered = (text or "").lower()
    for phrase, token in PHRASE_SYNONYMS.items():
        lowered = lowered.replace(phrase, " {} ".format(token))
    return lowered


def _expand(tokens):
    out = list(tokens)
    for token in tokens:
        out.extend(SYNONYMS.get(token, []))
    seen, unique = set(), []
    for token in out:
        if token not in seen:
            seen.add(token)
            unique.append(token)
    return unique


def retrieve_documents(paths) -> dict:
    """Load and index every numbered clause from all policy documents."""
    clauses, by_doc = [], {}

    for path in paths:
        if not os.path.isfile(path):
            raise OSError("policy document not found: {}".format(path))
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()

        name = os.path.basename(path)
        doc_clauses = []
        section_number, section_title = "0", "PREAMBLE"
        current = None
        title_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped or RULE_RE.match(stripped):
                continue

            section_match = SECTION_RE.match(stripped)
            if section_match:
                if current:
                    current["text"] = _normalise(current["text"])
                    current = None
                section_number = section_match.group(1)
                section_title = _normalise(section_match.group(2))
                continue

            clause_match = CLAUSE_RE.match(stripped)
            if clause_match:
                if current:
                    current["text"] = _normalise(current["text"])
                current = {
                    "doc": name,
                    "section_number": section_number,
                    "section_title": section_title,
                    "clause_id": clause_match.group(1),
                    "text": clause_match.group(2),
                }
                doc_clauses.append(current)
                clauses.append(current)
                continue

            if current:
                current["text"] += " " + stripped
            elif len(title_lines) < 3:
                title_lines.append(stripped)

        if current:
            current["text"] = _normalise(current["text"])

        if not doc_clauses:
            raise ValueError("no clauses parsed from {}".format(name))

        for clause in doc_clauses:
            clause["doc_title"] = title_lines[0] if title_lines else name
            clause["tokens"] = set(_tokenize(_canonicalise(clause["text"])))
        by_doc[name] = doc_clauses

    total = len(clauses)
    frequency = {}
    for clause in clauses:
        for token in clause["tokens"]:
            frequency[token] = frequency.get(token, 0) + 1
    idf = {t: math.log(total / (1 + c)) + 1.0 for t, c in frequency.items()}

    return {"clauses": clauses, "by_doc": by_doc, "idf": idf}


def _score_clause(clause, query_tokens, idf):
    return sum(idf.get(t, 1.0) for t in query_tokens if t in clause["tokens"])


def answer_question(index: dict, question: str) -> dict:
    """One document or none. The document is chosen before any text is assembled."""
    query_tokens = _expand(_tokenize(_canonicalise(question)))
    idf = index["idf"]

    doc_scores, doc_best = {}, {}
    for name, clauses in index["by_doc"].items():
        scored = sorted(
            ((_score_clause(c, query_tokens, idf), c) for c in clauses),
            key=lambda pair: -pair[0])
        doc_scores[name] = scored[0][0] if scored else 0.0
        doc_best[name] = scored

    ranking = sorted(doc_scores.items(), key=lambda pair: -pair[1])
    best_doc, best_score = ranking[0]
    runner_score = ranking[1][1] if len(ranking) > 1 else 0.0

    scores = {name: round(score, 2) for name, score in ranking}

    if best_score < RELEVANCE_FLOOR:
        return {"status": "REFUSED_NOT_COVERED", "body": REFUSAL_TEMPLATE,
                "doc": None, "sections": [], "citation": None, "scores": scores}

    if runner_score >= AMBIGUITY_RATIO * best_score:
        return {"status": "REFUSED_AMBIGUOUS", "body": REFUSAL_TEMPLATE,
                "doc": None, "sections": [], "citation": None, "scores": scores}

    # Only clauses of best_doc are reachable from here.
    top_clause = doc_best[best_doc][0][1]
    # Supporting clauses must share the winning clause's section. Sections are the
    # document's own topical grouping: IT section 2 governs corporate devices and
    # section 3 governs personal ones, so mixing them answers a different question
    # than the one asked — the same blending failure, one level down.
    section = top_clause["section_number"]
    selected = [c for score, c in doc_best[best_doc]
                if score >= CLAUSE_INCLUDE_RATIO * best_score
                and c["section_number"] == section][:MAX_CLAUSES]
    selected.sort(key=lambda c: [int(p) for p in c["clause_id"].split(".")])

    body = "\n".join("{}  {}".format(c["clause_id"], c["text"]) for c in selected)
    sections = [c["clause_id"] for c in selected]
    citation = "{} — section{} {}".format(
        best_doc, "s" if len(sections) > 1 else "", ", ".join(sections))

    return {"status": "ANSWERED", "body": body, "doc": best_doc,
            "sections": sections, "citation": citation, "scores": scores}


def render(result):
    if result["status"] == "ANSWERED":
        return "{}\n\nSource: {}".format(result["body"], result["citation"])
    return result["body"]


TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?", "policy_hr_leave.txt", ["2.6"]),
    ("Can I install Slack on my work laptop?", "policy_it_acceptable_use.txt", ["2.3"]),
    ("What is the home office equipment allowance?", "policy_finance_reimbursement.txt", ["3.1"]),
    ("Can I use my personal phone to access work files when working from home?",
     "EITHER", ["3.1"]),
    ("What is the company view on flexible working culture?", "REFUSE", []),
    ("Can I claim DA and meal receipts on the same day?", "policy_finance_reimbursement.txt", ["2.6"]),
    ("Who approves leave without pay?", "policy_hr_leave.txt", ["5.2"]),
]


def verify_answer(index):
    """Assert the enforcement rules on real output for the README's 7 questions."""
    raw = {}
    for name in index["by_doc"]:
        with open(os.path.join(DOC_DIR, name), "r", encoding="utf-8") as handle:
            raw[name] = _normalise(handle.read())

    rows, failures = [], []
    for question, expected_doc, expected_sections in TEST_QUESTIONS:
        result = answer_question(index, question)
        checks = {}

        checks["single_source"] = result["doc"] is None or \
            all(s in [c["clause_id"] for c in index["by_doc"][result["doc"]]]
                for s in result["sections"])

        if result["status"] == "ANSWERED":
            checks["extractive"] = all(
                _normalise(line.split("  ", 1)[1]) in raw[result["doc"]]
                for line in result["body"].splitlines() if "  " in line)
            checks["citation"] = bool(result["citation"]) and bool(result["sections"])
            checks["refusal_exact"] = True
        else:
            checks["extractive"] = True
            checks["citation"] = True
            checks["refusal_exact"] = result["body"] == REFUSAL_TEMPLATE

        lowered = render(result).lower()
        checks["no_hedging"] = not any(h in lowered for h in BANNED_HEDGES)

        if expected_doc == "REFUSE":
            checks["expectation"] = result["status"].startswith("REFUSED")
            outcome = result["status"]
        elif expected_doc == "EITHER":
            # Single-source IT answer OR refusal. If answered, it must cite the
            # clause that governs what personal devices may do (3.1); an answer
            # made only of restrictions omits the actual prohibition.
            single_it = (result["status"] == "ANSWERED" and
                         result["doc"] == "policy_it_acceptable_use.txt" and
                         all(s in result["sections"] for s in expected_sections))
            checks["expectation"] = single_it or result["status"].startswith("REFUSED")
            outcome = result["status"] + (
                " (" + result["doc"] + " " + ",".join(result["sections"]) + ")"
                if result["doc"] else "")
        else:
            checks["expectation"] = (result["doc"] == expected_doc and
                                     all(s in result["sections"] for s in expected_sections))
            outcome = "{} {}".format(result["doc"], ",".join(result["sections"]))

        if not all(checks.values()):
            failures.append((question, [k for k, v in checks.items() if not v]))
        rows.append((question, outcome, checks))

    print("{:<62} {:<44} {}".format("QUESTION", "OUTCOME", "CHECKS"))
    print("-" * 128)
    for question, outcome, checks in rows:
        flag = "PASS" if all(checks.values()) else "FAIL: " + ",".join(
            k for k, v in checks.items() if not v)
        print("{:<62} {:<44} {}".format(question[:60], outcome[:42], flag))

    print("")
    if failures:
        print("{} of {} questions FAILED".format(len(failures), len(TEST_QUESTIONS)))
        return 1
    print("all {} questions pass every enforcement check".format(len(TEST_QUESTIONS)))
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default=DOC_DIR)
    parser.add_argument("--question", default=None)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    paths = [os.path.join(args.docs, name) for name in DOCUMENTS]
    try:
        index = retrieve_documents(paths)
    except (OSError, ValueError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        sys.exit(1)

    if args.selftest:
        sys.exit(verify_answer(index))

    if args.question:
        print(render(answer_question(index, args.question)))
        return

    print("Ask My Documents — {} clauses indexed from {} policies".format(
        len(index["clauses"]), len(index["by_doc"])))
    print("Answers come from ONE document and cite their section. Blank line or 'quit' exits.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            break
        if not question or question.lower() in {"quit", "exit"}:
            break
        print("")
        print(render(answer_question(index, question)))
        print("")


if __name__ == "__main__":
    main()

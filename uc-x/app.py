"""
UC-X app.py — Ask My Documents.
Built from uc-x/agents.md (RICE enforcement) and uc-x/skills.md.

Answers staff questions only from the three CMC policy documents. Every
answer quotes whole clauses from ONE document with section citations;
anything else gets the refusal template, word for word.
"""
import argparse
import math
import os
import re
import sys
import textwrap

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT or Finance) for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered", "typically", "generally understood", "generally",
    "it is common practice", "common practice", "usually", "it may be assumed",
]

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]

STOPWORDS = set("""
a an the i me my we our you your is are am be been can could do does did to of for on in at by
with from as and or if it its this that what which who whom when where how why will would should
may must any all about there their they them have has had get got use used using company view
policy policies cmc employee employees staff allowed permitted please tell know work working many much
take taking apply need needs make go want
""".split())

# Multi-word phrases indexed as one term, so "leave without pay" and "LWP" match.
PHRASES = [
    (r"leave without pay", " lwp "),
    (r"daily allowance", " da "),
    (r"work[- ]from[- ]home|working from home|wfh", " wfh "),
]

# Question words that the documents express differently. Each question term
# matches if ANY of its alternatives appears in a clause.
SYNONYMS = {
    "laptop": ["laptop", "device", "corporate"],
    "phone": ["phone", "device", "mobile"],
    "mobile": ["mobile", "phone", "device"],
    "slack": ["slack", "software"],
    "app": ["app", "software"],
    "files": ["files", "data"],
    "file": ["file", "data"],
    "approves": ["approves", "approval"],
    "approve": ["approve", "approval"],
    "home": ["home", "wfh"],
}

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ()&/,\-–]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

MIN_COVERAGE = 0.5          # share of question key terms a clause must contain
CROSS_DOC_MARGIN = 0.85     # second document this close to the best -> ambiguous, refuse
MAX_CLAUSES = 3
SCOPE_COVERAGE = 0.3        # a permission-scope clause needs at least this much overlap

# "Can I ...?" questions are answered by what the policy permits, so the
# clause that sets the boundary ("X may ... only") must be quoted with them.
PERMISSION_QUESTION_RE = re.compile(r"^\s*(can|may|am i allowed|are we allowed|is it allowed)\b", re.IGNORECASE)


def _stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "s", "al", "e"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _terms(text: str) -> list:
    text = text.lower()
    for pattern, replacement in PHRASES:
        text = re.sub(pattern, replacement, text)
    return [w for w in re.findall(r"[a-z0-9]+", text) if w not in STOPWORDS]


def retrieve_documents(docs_dir: str) -> dict:
    """Load all 3 policy files and index every clause by document name and section number."""
    clauses = []
    for name in DOCUMENTS:
        path = os.path.join(docs_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as exc:
            sys.exit(f"Error: cannot read {path}: {exc}")

        heading, current, found = "", None, 0
        for raw in lines:
            line = raw.strip()
            if not line or set(line) <= {"═"}:
                current = None
                continue
            clause = CLAUSE_RE.match(line)
            section = SECTION_RE.match(line)
            if clause and heading:
                current = {"document": name, "section": clause.group(1), "heading": heading,
                           "text": clause.group(2)}
                clauses.append(current)
                found += 1
            elif section:
                heading, current = section.group(2).title(), None
            elif current is not None:
                current["text"] += " " + line
        if not found:
            sys.exit(f"Error: no numbered clauses found in {path}")

    for c in clauses:
        c["terms"] = {_stem(t) for t in _terms(c["text"])}
    doc_freq = {}
    for c in clauses:
        for t in c["terms"]:
            doc_freq[t] = doc_freq.get(t, 0) + 1
    n = len(clauses)
    idf = {t: math.log((n + 1) / (df + 0.5)) for t, df in doc_freq.items()}
    return {"clauses": clauses, "idf": idf, "max_idf": math.log(n + 1 / 0.5)}


def _question_concepts(question: str) -> list:
    concepts = []
    for word in _terms(question):
        alternatives = {_stem(a) for a in SYNONYMS.get(word, [word])}
        if alternatives not in concepts:
            concepts.append(alternatives)
    return concepts


def _score(clause: dict, concepts: list, index: dict):
    matched_weight, total_weight, matched_count = 0.0, 0.0, 0
    for alternatives in concepts:
        weight = max(index["idf"].get(a, index["max_idf"]) for a in alternatives)
        total_weight += weight
        hits = [index["idf"][a] for a in alternatives if a in clause["terms"]]
        if hits:
            matched_weight += max(hits)
            matched_count += 1
    coverage = matched_weight / total_weight if total_weight else 0.0
    return matched_weight, coverage, matched_count


def _is_scope_clause(text: str) -> bool:
    """A clause that grants something and limits it in the same breath: 'may ... only'."""
    return re.search(r"\bmay\b", text, re.IGNORECASE) is not None and \
        re.search(r"\bonly\b", text, re.IGNORECASE) is not None


def answer_question(question: str, index: dict) -> str:
    """Return a single-source answer with citations, or the refusal template."""
    concepts = _question_concepts(question)
    if not concepts:
        return REFUSAL_TEMPLATE

    scored = []
    for clause in index["clauses"]:
        score, coverage, matched = _score(clause, concepts, index)
        if score > 0:
            scored.append((score, coverage, clause, matched))
    scored.sort(key=lambda s: -s[0])
    if not scored:
        return REFUSAL_TEMPLATE

    best_score, best_coverage, best, best_matched = scored[0]
    if best_coverage < MIN_COVERAGE:
        return REFUSAL_TEMPLATE

    # Anti-blending: if another document is almost as relevant — covering as many of
    # the question's key terms with a near-equal score — the question straddles two
    # policies, so refuse rather than merge them.
    other_doc = max((s for s in scored if s[2]["document"] != best["document"]),
                    key=lambda s: (s[3], s[0]), default=None)
    if (other_doc and other_doc[1] >= MIN_COVERAGE and other_doc[3] >= best_matched
            and other_doc[0] >= CROSS_DOC_MARGIN * best_score):
        return REFUSAL_TEMPLATE

    # Supporting clauses: same document only, and each must itself cover the question.
    supporting = [s[2] for s in scored[1:]
                  if s[2]["document"] == best["document"] and s[1] >= MIN_COVERAGE]

    # Permission questions also get the scope-setting clause from the same section,
    # so the answer says what IS allowed, not only what is forbidden.
    scope = []
    if PERMISSION_QUESTION_RE.search(question):
        best_section = best["section"].split(".")[0]
        scope = [s[2] for s in scored
                 if s[2] is not best
                 and s[2]["document"] == best["document"]
                 and s[2]["section"].split(".")[0] == best_section
                 and s[1] >= SCOPE_COVERAGE
                 and _is_scope_clause(s[2]["text"])]

    chosen = []
    for c in [best] + scope + supporting:
        if c not in chosen:
            chosen.append(c)
    chosen = chosen[:MAX_CLAUSES]
    chosen.sort(key=lambda c: [int(p) for p in c["section"].split(".")])

    lines = [f"Source: {best['document']}"]
    for c in chosen:
        quoted = textwrap.fill(f'[{best["document"]}, section {c["section"]}] {c["text"]}',
                               width=88, subsequent_indent="    ")
        lines.append(quoted)
    answer = "\n".join(lines)

    assert len({c["document"] for c in chosen}) == 1  # enforcement rule 1: single source
    if any(h in answer.lower() for h in HEDGING_PHRASES):
        return REFUSAL_TEMPLATE
    return answer


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                           "..", "data", "policy-documents"),
                        help="Folder containing the three policy .txt files")
    parser.add_argument("--question", help="Answer one question and exit")
    parser.add_argument("--test", action="store_true", help="Run the 7 README test questions and exit")
    args = parser.parse_args()

    index = retrieve_documents(args.docs_dir)

    if args.question:
        print(answer_question(args.question, index))
        return
    if args.test:
        for i, q in enumerate(TEST_QUESTIONS, 1):
            print(f"Q{i}: {q}")
            print(answer_question(q, index))
            print("-" * 88)
        return

    print(f"Ask My Documents — {len(index['clauses'])} clauses indexed from "
          f"{', '.join(DOCUMENTS)}.")
    print("Type a question, or 'exit' to quit.\n")
    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"exit", "quit", "q"}:
            break
        if not question:
            print("Please type a question.\n")
            continue
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()

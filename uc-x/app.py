"""
UC-X — Ask My Documents
Implements the enforcement rules in agents.md and the two skills in skills.md.

Failure modes taught: cross-document blending, hedged hallucination, condition
dropping. This implementation answers from exactly ONE document's section group,
returns the full clause text (so conditions cannot be dropped), cites document +
section on every claim, and returns the exact refusal template when no single
document distinctively covers the question.

Skills:
  retrieve_documents -> load 3 policy files, index by document name + section number
  answer_question    -> single-source answer with citations, or exact refusal template

Usage:
  python app.py               # interactive CLI
  python app.py --selftest    # run the 7 canonical README questions
"""
import argparse
import math
import os
import re
import sys

DOC_DIR = os.path.join("..", "data", "policy-documents")
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")
SEPARATOR_CHARS = set("═=─-")

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "to", "of",
    "on", "in", "at", "for", "and", "or", "but", "if", "then", "than", "with", "as",
    "by", "from", "into", "this", "that", "these", "those", "it", "its", "i", "you",
    "my", "me", "we", "our", "can", "could", "should", "would", "may", "might", "will",
    "shall", "do", "does", "did", "done", "have", "has", "had", "what", "who", "when",
    "where", "why", "how", "which", "whom", "use", "used", "using", "get", "got",
    "am", "any", "all", "there", "here", "about", "so", "not", "no", "yes", "up",
}

DISTINCTIVE_DF_RATIO = 0.30   # a stem is "distinctive" if it appears in <=30% of clauses
AMBIGUITY_RATIO = 0.70        # refuse if a runner-up from another document scores this close
MIN_ANSWER_SCORE = 3.0        # refuse if the best match is too weak to be a real answer

# Longest-first suffixes for a light stemmer. A suffix is stripped only if at least
# 4 characters remain, so short words are left intact. This lets work/working and
# approve/approval/approved collapse together while keeping company != computers.
SUFFIXES = ["ational", "ization", "ements", "ments", "ment", "tions", "tion",
            "ings", "ing", "edly", "ed", "es", "s", "ly", "al"]


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and all(ch in SEPARATOR_CHARS for ch in stripped)


def _stem(token: str) -> str:
    for suf in SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 4:
            return token[: -len(suf)]
    return token


def _tokens(text: str):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def _stems(text: str):
    return {_stem(t) for t in _tokens(text)}


def retrieve_documents(doc_dir: str, doc_files):
    """
    Load the policy files and index them into section groups with term statistics.
    Returns: (groups, df) where groups is a list of section-group dicts and df maps
    stem -> number of clauses containing it.
    """
    groups = []
    all_clause_stems = []  # one stem-set per clause, for df computation

    for fname in doc_files:
        path = os.path.join(doc_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            raise RuntimeError(f"Could not read policy document '{path}': {exc}") from exc

        current_group = None
        current_clause = None

        def _flush_clause():
            nonlocal current_clause
            if current_clause is not None:
                current_clause["text"] = re.sub(r"\s+", " ", current_clause["text"]).strip()
                stems = _stems(current_group["title"] + " " + current_clause["text"])
                current_clause["stems"] = stems
                all_clause_stems.append(stems)
                current_group["clauses"].append(current_clause)
                current_clause = None

        for line in lines:
            if _is_separator(line) or not line.strip():
                continue
            section_match = SECTION_RE.match(line)
            clause_match = CLAUSE_RE.match(line)

            if section_match and not clause_match:
                _flush_clause()
                current_group = {
                    "doc": fname,
                    "section": section_match.group(1),
                    "title": section_match.group(2).strip(),
                    "clauses": [],
                }
                groups.append(current_group)
            elif clause_match and current_group is not None:
                _flush_clause()
                current_clause = {"ref": clause_match.group(1), "text": clause_match.group(2)}
            elif current_clause is not None:
                current_clause["text"] += " " + line.strip()

        _flush_clause()

    # Document frequency per stem, across all clauses.
    df = {}
    for stems in all_clause_stems:
        for s in stems:
            df[s] = df.get(s, 0) + 1

    return groups, df, len(all_clause_stems)


def _score_groups(index, question: str):
    """Return groups scored against the question, sorted high-to-low, each with a
    distinctive-match flag."""
    groups, df, n_clauses = index
    q_stems = _stems(question)
    if not q_stems:
        return []

    idf = {s: math.log(n_clauses / (1 + df.get(s, 0))) for s in q_stems}
    distinctive_cap = DISTINCTIVE_DF_RATIO * n_clauses

    scored = []
    for group in groups:
        # Count each matched query stem ONCE per group (not per clause), so a large
        # section cannot win simply by repeating a common word like "work"/"home".
        group_stems = set()
        for clause in group["clauses"]:
            group_stems |= clause["stems"]
        matched = {s for s in q_stems if s in group_stems}
        if not matched:
            continue
        score = sum(max(idf[s], 0.0) for s in matched)
        has_distinctive = any(df.get(s, 0) <= distinctive_cap for s in matched)
        scored.append({"group": group, "score": score, "distinctive": has_distinctive})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def answer_question(index, question: str, debug: bool = False) -> str:
    """
    Return a single-source, cited answer, or the exact refusal template.
    """
    scored = _score_groups(index, question)

    if debug:
        for s in scored[:3]:
            sys.stderr.write(
                f"  [debug] {s['score']:.2f} distinctive={s['distinctive']} "
                f"{s['group']['doc']} §{s['group']['section']}\n"
            )

    # Enforcement: refuse unless a single group distinctively AND strongly covers
    # the question (too-weak matches are hedged hallucination waiting to happen).
    if (not scored or not scored[0]["distinctive"]
            or scored[0]["score"] < MIN_ANSWER_SCORE):
        return REFUSAL_TEMPLATE

    best = scored[0]
    # Enforcement: refuse on cross-document ambiguity — if a runner-up from a
    # DIFFERENT document scores nearly as high, answering would risk blending.
    for other in scored[1:]:
        if other["group"]["doc"] != best["group"]["doc"]:
            if other["score"] >= AMBIGUITY_RATIO * best["score"]:
                return REFUSAL_TEMPLATE
            break

    group = best["group"]
    # Answer from the winning group's document ONLY — never blend.
    lines = [f"According to {group['doc']} (§ {group['section']} {group['title']}):", ""]
    for clause in group["clauses"]:
        lines.append(f"  {group['doc']} § {clause['ref']}: {clause['text']}")
    return "\n".join(lines)


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
    parser.add_argument("--doc-dir", default=DOC_DIR, help="Directory of policy .txt files")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 canonical README questions and exit")
    parser.add_argument("--debug", action="store_true",
                        help="Print top group scores to stderr (calibration aid)")
    args = parser.parse_args()

    try:
        index = retrieve_documents(args.doc_dir, DOC_FILES)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.selftest:
        for q in SELFTEST_QUESTIONS:
            print("=" * 70)
            print(f"Q: {q}")
            print("-" * 70)
            print(answer_question(index, q, debug=args.debug))
            print()
        return

    print("Ask a question about the policy documents. Type 'exit' or 'quit' to stop.")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        print(answer_question(index, question))


if __name__ == "__main__":
    main()

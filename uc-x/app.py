"""
UC-X - Ask My Documents

Implements the enforcement rules declared in uc-x/agents.md:

  SINGLE-SOURCE ANSWERS     every answer is drawn from exactly one document; two documents never merge
  NO HEDGING                answer text is verbatim clause text; banned phrases are checked before print
  EXACT REFUSAL TEMPLATE    out-of-scope questions get one fixed string, no per-question variation
  CITE DOCUMENT AND SECTION every factual line carries its file name and clause number
  REFUSE ON CONTEST         when two documents are equally relevant, neither is used

Standard library only. Deterministic: the same question always returns the same answer.

Usage:
    python app.py                          # interactive
    python app.py --question "..."         # single question
    python app.py --selftest               # run the 7 README test questions
"""

import argparse
import math
import os
import re
import sys
from typing import Dict, List, Tuple

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

DEFAULT_DOC_DIR = os.path.join("..", "data", "policy-documents")

# --------------------------------------------------------------------------
# EXACT REFUSAL TEMPLATE
# One fixed string. The team is not inferred per question: working out which
# department owns an uncovered topic means guessing what the question is about,
# which is the exact behaviour the refusal exists to prevent.
# --------------------------------------------------------------------------

REFUSAL_NOT_COVERED = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

# A distinct condition needs a distinct answer. The question IS covered here -
# saying it is not would be false - but two documents speak to it and combining
# them would invent a permission neither one grants.
REFUSAL_CROSS_DOCUMENT = (
    "This question touches {doc_a} and {doc_b}, and answering it would require\n"
    "combining claims from both. Those claims are not combined here, because a merged\n"
    "answer states a rule that neither document contains.\n"
    "Please raise this with the owners of both policies before proceeding."
)

# --------------------------------------------------------------------------
# NO HEDGING - checked against the printed answer, not merely promised.
# --------------------------------------------------------------------------

BANNED_PHRASES = [
    "while not explicitly covered",
    "not explicitly covered",
    "typically",
    "generally understood",
    "generally speaking",
    "it is common practice",
    "common practice",
    "usually",
    "in most cases",
    "it is likely",
    "should be fine",
    "as a rule of thumb",
    "broadly speaking",
]

# --------------------------------------------------------------------------
# Retrieval configuration. These affect WHICH clause is found, never what the
# answer says - answer text is always the clause reproduced verbatim.
# --------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "am",
    "i", "me", "my", "we", "our", "you", "your", "it", "its", "they", "them",
    "this", "that", "these", "those", "and", "or", "but", "if", "then", "than",
    "of", "to", "in", "on", "at", "for", "from", "by", "with", "as", "about",
    "can", "could", "may", "might", "will", "would", "shall", "should", "must",
    "do", "does", "did", "have", "has", "had", "what", "when", "where", "who",
    "whom", "which", "how", "why", "any", "some", "there", "here", "get", "got",
    "need", "want", "use", "using", "used", "same", "also", "not", "no", "yes",
    "company", "cmc", "corporation", "municipal", "employee", "employees",
    "policy", "view", "allowed", "allow",
}

# Retrieval-only synonyms. Declared as a constant so a reviewer can object to
# any entry. Expanding "phone" to "device" changes which clause is retrieved;
# it never adds a word to the answer.
SYNONYMS = {
    "phone": ["device", "mobile", "smartphone"],
    "phones": ["device", "mobile", "smartphone"],
    "mobile": ["phone", "device"],
    "laptop": ["device"],
    "laptops": ["device"],
    "file": ["data", "document"],
    "files": ["data", "document"],
    "lwp": ["leave", "without", "pay"],
    "wfh": ["work-from-home", "home"],
    "app": ["software"],
    "apps": ["software"],
    "slack": ["software", "install"],
    "install": ["software"],
    "software": ["install", "installation"],
    "approve": ["approval"],
    "approves": ["approval"],
    "sick": ["medical"],
    "reimburse": ["reimbursement", "reimbursable"],
    "reimbursed": ["reimbursement", "reimbursable"],
    "da": ["allowance"],
}

MIN_TERMS_MATCHED = 2      # a single incidental word is not a topic match
MIN_SCORE = 3.0            # relevance floor below which the refusal template fires
SINGLE_SOURCE_MARGIN = 0.80  # runner-up document this close means the question is contested
MAX_CLAUSES_IN_ANSWER = 4


def _stem(token: str) -> str:
    """Crude normaliser so 'approves', 'approved' and 'approval' meet at 'approv'.

    Plurals are folded first, then derivational suffixes, then a trailing 'e'.
    That last step matters: without it 'device' and 'devices' land on different
    stems and a clause that plainly answers the question scores zero for it.
    """
    if len(token) > 4 and token.endswith("ies"):
        token = token[:-3] + "y"
    elif len(token) > 4 and token.endswith("es"):
        base = token[:-2]
        token = base if base.endswith(("s", "x", "z", "ch", "sh")) else token[:-1]
    elif len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]

    for suffix in ("ation", "ing", "able", "al", "ed"):
        if len(token) - len(suffix) >= 4 and token.endswith(suffix):
            token = token[: -len(suffix)]
            break

    if len(token) > 4 and token.endswith("e"):
        token = token[:-1]
    return token


def _terms(text: str, expand: bool = False) -> List[str]:
    raw = re.findall(r"[A-Za-z][A-Za-z\-]{1,}", (text or "").lower())
    out: List[str] = []
    for token in raw:
        token = token.strip("-")
        if not token or token in STOPWORDS:
            continue
        out.append(_stem(token))
        if expand:
            for synonym in SYNONYMS.get(token, []):
                out.append(_stem(synonym))
    return out


# --------------------------------------------------------------------------
# Skill: retrieve_documents
# --------------------------------------------------------------------------

def retrieve_documents(doc_dir: str) -> dict:
    """Load all three policy files and index them by document and clause number."""
    section_re = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s\-()/&,]+)\s*$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    separator_re = re.compile(r"^[\u2550\u2500=\-_]{5,}\s*$")

    clauses: List[dict] = []
    loaded: List[str] = []

    for name in DOCUMENTS:
        path = os.path.join(doc_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                raw = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            sys.stderr.write("ERROR: could not read {}: {}\n".format(path, exc))
            sys.exit(1)

        current_section_title = ""
        current = None
        seen_section = False

        def close(current, section_title):
            if current is not None:
                current["text"] = re.sub(r"\s+", " ", current["text"]).strip()
                current["section_title"] = section_title
                clauses.append(current)

        for line in raw.replace("\r\n", "\n").split("\n"):
            stripped = line.strip()
            if not stripped or separator_re.match(stripped):
                continue

            section_match = section_re.match(stripped)
            if section_match:
                close(current, current_section_title)
                current = None
                seen_section = True
                current_section_title = section_match.group(2).strip()
                continue

            clause_match = clause_re.match(stripped)
            if clause_match:
                close(current, current_section_title)
                current = {
                    "document": name,
                    "id": clause_match.group(1),
                    "text": clause_match.group(2),
                }
                continue

            if current is not None:
                current["text"] += " " + stripped
            elif not seen_section:
                continue

        close(current, current_section_title)
        loaded.append(name)

    if not clauses:
        sys.stderr.write("ERROR: no clauses parsed from {}\n".format(doc_dir))
        sys.exit(1)

    # The section title is indexed for retrieval but never shown in the answer.
    # It is how "Who approves leave without pay?" reaches clause 5.2, whose own
    # text says only "LWP".
    total = len(clauses)
    document_frequency: Dict[str, int] = {}
    for clause in clauses:
        clause["index_terms"] = set(
            _terms(clause["section_title"] + " " + clause["text"]))
        for term in clause["index_terms"]:
            document_frequency[term] = document_frequency.get(term, 0) + 1

    idf = {term: math.log(total / (1.0 + count)) + 1.0
           for term, count in document_frequency.items()}

    return {"clauses": clauses, "idf": idf, "documents": loaded, "total": total}


# --------------------------------------------------------------------------
# Skill: score_clauses
# --------------------------------------------------------------------------

def score_clauses(index: dict, question: str) -> List[Tuple[dict, float, int]]:
    """Rank every clause against the question by IDF-weighted term overlap."""
    query = set(_terms(question, expand=True))
    if not query:
        return []

    scored = []
    for clause in index["clauses"]:
        matched = query & clause["index_terms"]
        if not matched:
            continue
        score = sum(index["idf"].get(term, 1.0) for term in matched)
        scored.append((clause, score, len(matched)))

    scored.sort(key=lambda item: (-item[1], item[0]["document"], item[0]["id"]))
    return scored


# --------------------------------------------------------------------------
# Skill: answer_question
# --------------------------------------------------------------------------

def answer_question(index: dict, question: str) -> dict:
    """Return a single-source answer with citations, or a refusal.

    Never returns clauses from more than one document.
    """
    scored = score_clauses(index, question)

    if not scored:
        return {"status": "REFUSED_NOT_COVERED", "text": REFUSAL_NOT_COVERED,
                "citations": [], "document": ""}

    top_clause, top_score, top_matched = scored[0]

    # Relevance floor: an incidental word in common is not coverage.
    if top_score < MIN_SCORE or top_matched < MIN_TERMS_MATCHED:
        return {"status": "REFUSED_NOT_COVERED", "text": REFUSAL_NOT_COVERED,
                "citations": [], "document": ""}

    # Best score per document decides which single document may be used.
    best_per_document: Dict[str, float] = {}
    for clause, score, _ in scored:
        name = clause["document"]
        if score > best_per_document.get(name, 0.0):
            best_per_document[name] = score

    ranked_documents = sorted(best_per_document.items(), key=lambda kv: -kv[1])
    winner, winner_score = ranked_documents[0]

    # REFUSE ON CONTEST: a close runner-up document means answering would mean
    # choosing between two sources, or worse, merging them.
    if len(ranked_documents) > 1:
        runner_up, runner_up_score = ranked_documents[1]
        if runner_up_score >= winner_score * SINGLE_SOURCE_MARGIN:
            return {
                "status": "REFUSED_CROSS_DOCUMENT",
                "text": REFUSAL_CROSS_DOCUMENT.format(doc_a=winner, doc_b=runner_up),
                "citations": [], "document": "",
            }

    # SINGLE-SOURCE: everything below comes from `winner` and nowhere else.
    selected = [(c, s) for c, s, _ in scored
                if c["document"] == winner and s >= winner_score * 0.55]
    selected = selected[:MAX_CLAUSES_IN_ANSWER]
    selected.sort(key=lambda item: [int(p) for p in item[0]["id"].split(".")])

    lines = []
    citations = []
    for clause, _ in selected:
        lines.append("  [{}] {}".format(clause["id"], clause["text"]))
        citations.append("{}, section {}".format(winner, clause["id"]))

    return {
        "status": "ANSWERED",
        "text": "\n".join(lines),
        "citations": citations,
        "document": winner,
    }


# --------------------------------------------------------------------------
# NO HEDGING - verified on the rendered output.
# --------------------------------------------------------------------------

def check_no_hedging(text: str) -> List[str]:
    lowered = text.lower()
    return [phrase for phrase in BANNED_PHRASES if phrase in lowered]


def render(result: dict) -> str:
    out = []
    if result["status"] == "ANSWERED":
        out.append("ANSWER - source: {}".format(result["document"]))
        out.append(result["text"])
        out.append("")
        out.append("CITATIONS:")
        for citation in result["citations"]:
            out.append("  - {}".format(citation))
        out.append("")
        out.append("Answered from {} only. No clause from any other document was "
                   "combined into this answer.".format(result["document"]))
    elif result["status"] == "REFUSED_CROSS_DOCUMENT":
        out.append("REFUSED - cross-document question")
        out.append(result["text"])
    else:
        out.append("REFUSED - not covered")
        out.append(result["text"])

    rendered = "\n".join(out)

    hedges = check_no_hedging(rendered)
    if hedges:
        # Fail loudly rather than print a hedged answer.
        sys.stderr.write("ERROR: hedging phrase(s) in output: {}\n".format(hedges))
        sys.exit(1)
    return rendered


# --------------------------------------------------------------------------

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
    parser.add_argument("--docs", default=DEFAULT_DOC_DIR,
                        help="Directory holding the three policy .txt files")
    parser.add_argument("--question", help="Answer one question and exit")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)
    sys.stderr.write("Indexed {} clauses from {} documents.\n".format(
        index["total"], len(index["documents"])))

    if args.selftest:
        for number, question in enumerate(SELFTEST_QUESTIONS, start=1):
            print("=" * 74)
            print("Q{}: {}".format(number, question))
            print("-" * 74)
            print(render(answer_question(index, question)))
            print()
        return

    if args.question:
        print(render(answer_question(index, args.question)))
        return

    print("Ask My Documents - policy Q&A over:")
    for name in index["documents"]:
        print("  - {}".format(name))
    print("Type a question, or 'quit' to exit.\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            return
        print()
        print(render(answer_question(index, question)))
        print()


if __name__ == "__main__":
    main()
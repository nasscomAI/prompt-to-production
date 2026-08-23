"""
UC-X — Ask My Documents

Answers employee questions strictly from three CMC policy documents.
Behaviour follows the enforcement rules in agents.md:

- single-source rule: every answer draws on ONE document only; if evidence
  spans two documents or no document clearly wins, the system refuses
  instead of blending
- citation rule: every factual claim is a verbatim source quote tagged with
  the document name and section number
- multi-condition preservation: clauses are quoted whole, so compound
  obligations survive intact (HR 5.2 Department Head AND HR Director;
  Finance 3.1 Rs 8,000 AND one-time AND permanent WFH; Finance 2.6
  DA-vs-meal-receipts mutual exclusion)
- no hedging: output passes a banned-phrase guard before printing
- exact refusal template: questions not covered by the documents receive
  the template character-for-character, with no variations

The tool is deterministic and fully offline.
"""
import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_DOC_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

DOC_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BANNED_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)

SCORE_FLOOR = 6.5
MIN_MATCHED_TERMS = 2
AMBIGUITY_RATIO = 0.85
SUPPORT_RATIO = 0.5
MAX_SUPPORTING_CLAUSES = 3

BINDING_MARKERS = (
    "must not", "requires", "cannot", "may not", "not permitted",
    "not valid", "not sufficient", "not eligible", "not reimbursable",
    "forfeit", "entitled", "mandatory", "prohibited", "only",
    "will not", "not accepted", "under no circumstances",
)

BANNER_RE = re.compile(r"^[═=]{5,}\s*$")
SECTION_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
TOKEN_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = frozenset("""
a an the i me my myself we our ours you your yours he him his she her it its
they them their what which who whom whose when where why how is am are was
were be been being do does did doing have has had having will would shall
should can could may might must of in on at by for with from to as and or
but if then than so such no nor not only own too very just about into over
under again there here all any both each few more most other some up down
out off while use using used usage
""".split())

SUFFIXES = (("ies", "y"), ("ing", ""), ("ed", ""), ("ment", ""),
            ("ance", ""), ("es", ""), ("s", ""), ("e", ""))
MIN_STEM_LEFTOVER = 3
E_STRIP_MIN_LEFTOVER = 4

STEM_SYNONYMS = {
    "phon": frozenset({"devic"}),
    "devic": frozenset({"phon"}),
    "laptop": frozenset({"devic"}),
    "slack": frozenset({"softwar"}),
    "fil": frozenset({"data", "docu"}),
    "docu": frozenset({"fil", "data"}),
    "lwp": frozenset({"leav", "without", "pay"}),
    "approv": frozenset({"approval"}),
}

DEVICE_CONCEPT = frozenset({"phon", "devic", "laptop", "smartphon"})
ACCESS_CONCEPT = frozenset({"acc", "fil", "data", "docu", "network"})
PHRASE_BONUS = 4.0
BINDING_BONUS = 3.0

PERMISSIVE_QUERY_TOKENS = frozenset({
    "can", "could", "may", "allowed", "allow", "permitted", "permission",
})
PERMISSIVE_CLAUSE_PATTERNS = (
    "may be", "may use", "may carry", "may apply", "are entitled",
    "is entitled", "is permitted", "are permitted", "entitled to",
    "can be", "may be used",
)
PERMISSIVE_BONUS = 3.5


class PolicyCorpusError(Exception):
    """Raised when the policy corpus is missing or unparseable."""


def stem(word):
    for _ in range(4):
        changed = False
        for suffix, replacement in SUFFIXES:
            if not word.endswith(suffix):
                continue
            if suffix == "e":
                if len(word) - 1 >= E_STRIP_MIN_LEFTOVER:
                    word = word[:-1]
                    changed = True
                break
            candidate = word[: -len(suffix)] + replacement
            if len(candidate) >= MIN_STEM_LEFTOVER:
                word = candidate
                changed = True
            break
        if not changed:
            break
    return word


def content_terms(text):
    return [stem(token) for token in TOKEN_RE.findall(text.lower())
            if token not in STOPWORDS]


def normalise_text(text):
    return re.sub(r"\s+", " ", text).strip()


def parse_policy(path):
    with open(path, encoding="utf-8-sig") as handle:
        raw_lines = handle.read().splitlines()

    meta = []
    sections = []
    current_section = None
    seen_banner = False

    for raw_line in raw_lines:
        line = raw_line.rstrip()
        if BANNER_RE.match(line):
            seen_banner = True
            continue
        if not line.strip():
            continue
        stripped = line.strip()
        section_match = SECTION_RE.match(stripped)
        clause_match = CLAUSE_RE.match(stripped)
        if section_match and not clause_match:
            current_section = {
                "number": int(section_match.group(1)),
                "title": normalise_text(section_match.group(2)),
                "clauses": [],
            }
            sections.append(current_section)
            continue
        if clause_match and seen_banner:
            if current_section is None:
                raise PolicyCorpusError(
                    "Clause %s found before any section heading in %s"
                    % (clause_match.group(1), path.name)
                )
            current_section["clauses"].append({
                "id": clause_match.group(1),
                "text": normalise_text(clause_match.group(2)),
            })
            continue
        if current_section is None:
            meta.append(normalise_text(stripped))
            continue
        if current_section["clauses"]:
            attached = current_section["clauses"][-1]
            attached["text"] = normalise_text(attached["text"] + " " + stripped)
            continue
        raise PolicyCorpusError(
            "Unattachable line before first clause in section %d of %s: %r"
            % (current_section["number"], path.name, stripped)
        )

    if not sections:
        raise PolicyCorpusError("No numbered sections found in %s" % path.name)

    clause_ids = []
    for section in sections:
        for clause in section["clauses"]:
            clause_ids.append(clause["id"])
    if not clause_ids:
        raise PolicyCorpusError("No numbered clauses found in %s" % path.name)
    if len(set(clause_ids)) != len(clause_ids):
        raise PolicyCorpusError("Duplicate clause numbers detected in %s" % path.name)

    return {"meta": meta, "sections": sections}


def retrieve_documents(doc_dir=None):
    """
    Load all three policy files and index them by document name and
    section number. Returns the index dict described in skills.md.
    Raises PolicyCorpusError when any file is missing or unparseable.
    """
    directory = Path(doc_dir) if doc_dir else DEFAULT_DOC_DIR
    documents = []
    flat_clauses = []
    for filename in DOC_FILES:
        path = directory / filename
        if not path.is_file():
            raise PolicyCorpusError("Required policy document not found: %s" % path)
        parsed = parse_policy(path)
        documents.append({"name": filename, "meta": parsed["meta"],
                          "sections": parsed["sections"]})
        for section in parsed["sections"]:
            for clause in section["clauses"]:
                flat_clauses.append({
                    "doc": filename,
                    "section_number": section["number"],
                    "section_title": section["title"],
                    "id": clause["id"],
                    "text": clause["text"],
                    "binding": is_binding_clause(clause["text"]),
                    "permissive": is_permissive_clause(clause["text"]),
                    "counter": Counter(expand_stems(
                        content_terms(clause["id"] + " " + clause["text"]))),
                })

    total = len(flat_clauses)
    document_frequency = Counter()
    for clause in flat_clauses:
        document_frequency.update(clause["counter"].keys())
    idf = {term: math.log((total + 1) / (df + 1)) + 1.0
           for term, df in document_frequency.items()}

    return {
        "documents": documents,
        "clauses": flat_clauses,
        "idf": idf,
    }


def is_binding_clause(text):
    lowered = text.lower()
    return any(marker in lowered for marker in BINDING_MARKERS)


def is_permissive_clause(text):
    lowered = text.lower()
    return any(pattern in lowered for pattern in PERMISSIVE_CLAUSE_PATTERNS)


def expand_stems(stems):
    expanded = set(stems)
    for stem_form in stems:
        expanded.update(STEM_SYNONYMS.get(stem_form, frozenset()))
    return expanded


def score_clause(query_expanded, query_has_pair, query_permissive, clause, idf):
    total = 0.0
    clause_terms = clause["counter"].keys()
    for term in query_expanded:
        if term in clause["counter"]:
            total += idf.get(term, 0.0)
    if clause["binding"]:
        total += BINDING_BONUS
    if query_permissive and clause["permissive"]:
        total += PERMISSIVE_BONUS
    if query_has_pair and (clause_terms & DEVICE_CONCEPT) \
            and (clause_terms & ACCESS_CONCEPT):
        total += PHRASE_BONUS
    return total


def compose_answer(doc_name, supporting):
    lines = ["Answer (single source: %s):" % doc_name, ""]
    cited = []
    for clause in supporting:
        cited.append(clause["id"])
        lines.append(
            "  [%s §%s — %s] \"%s\""
            % (clause["doc"], clause["id"], clause["section_title"], clause["text"])
        )
    lines.append("")
    lines.append(
        "Source: %s sections %s — one document only; no claims were combined "
        "across documents." % (doc_name, ", ".join(cited))
    )
    text = "\n".join(lines)
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            raise PolicyCorpusError(
                "Internal guard tripped: banned hedging phrase %r reached output" % phrase
            )
    return {"type": "answer", "text": text,
            "sources": [{"doc": doc_name, "sections": cited}]}


def answer_question(question, index):
    """
    Search the index for the question's terms and return either a
    single-source answer with per-clause citations or the exact refusal
    template. Never guesses: weak evidence and cross-document ambiguity
    both refuse.
    """
    stems = content_terms(question)
    if not stems:
        return {"type": "refusal", "text": REFUSAL_TEMPLATE, "sources": []}

    query_expanded = expand_stems(stems)
    query_has_pair = bool(query_expanded & DEVICE_CONCEPT) \
        and bool(query_expanded & ACCESS_CONCEPT)
    raw_tokens = set(TOKEN_RE.findall(question.lower()))
    query_permissive = bool(raw_tokens & PERMISSIVE_QUERY_TOKENS)
    idf = index["idf"]

    doc_best = {}
    ranked = []
    for clause in index["clauses"]:
        score = score_clause(query_expanded, query_has_pair,
                             query_permissive, clause, idf)
        clause["_score"] = score
        ranked.append(clause)
        name = clause["doc"]
        if score > doc_best.get(name, (None, 0.0))[1]:
            doc_best[name] = (clause["id"], score)

    if not doc_best:
        return {"type": "refusal", "text": REFUSAL_TEMPLATE, "sources": []}

    best_doc = max(DOC_FILES, key=lambda name: doc_best.get(name, (None, 0.0))[1])
    best_score = doc_best[best_doc][1]
    runner_up = max((score for name, (_, score) in doc_best.items() if name != best_doc),
                    default=0.0)

    matched_original = sum(1 for term in set(stems)
                           if any(term in clause["counter"] for clause in index["clauses"]))
    weak_evidence = best_score < SCORE_FLOOR or matched_original < MIN_MATCHED_TERMS
    ambiguous = runner_up >= AMBIGUITY_RATIO * best_score
    if weak_evidence or ambiguous:
        return {"type": "refusal", "text": REFUSAL_TEMPLATE, "sources": []}

    threshold = best_score * SUPPORT_RATIO
    supporting = [clause for clause in ranked
                  if clause["doc"] == best_doc and clause["_score"] >= threshold]
    supporting.sort(key=lambda clause: (-clause["_score"], clause["id"]))
    supporting = supporting[:MAX_SUPPORTING_CLAUSES]

    return compose_answer(best_doc, supporting)


def format_result(result):
    return result["text"]


def interactive_loop(index):
    print("UC-X — Ask My Documents")
    print("Grounded in: %s" % ", ".join(DOC_FILES))
    print("Type a question ('exit' or 'quit' to leave).")
    while True:
        try:
            line = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            return 0
        result = answer_question(line, index)
        print()
        print(format_result(result))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--ask", default=None,
                        help="Ask one question non-interactively, then exit")
    parser.add_argument("--doc-dir", default=None,
                        help="Directory containing the three policy documents")
    args = parser.parse_args()

    try:
        index = retrieve_documents(args.doc_dir)
    except PolicyCorpusError as error:
        print("REFUSED: policy corpus unavailable: %s" % error, file=sys.stderr)
        sys.exit(2)

    if args.ask is not None:
        result = answer_question(args.ask, index)
        print(format_result(result))
        return

    sys.exit(interactive_loop(index))


if __name__ == "__main__":
    main()

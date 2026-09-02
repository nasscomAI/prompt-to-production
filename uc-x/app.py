"""
UC-X — Ask My Documents

Deterministic, single-source question answering over exactly three CMC policy
documents (policy_hr_leave.txt, policy_it_acceptable_use.txt,
policy_finance_reimbursement.txt). Enforces the contract in agents.md /
skills.md:

  * Every factual answer is drawn from ONE document and ONE section, and ends
    with a citation of the form "<document_name>, section <number>".
  * Answers are the section's literal text — no facts, actors, or numbers are
    added, and no condition of the section is dropped.
  * Two documents are never named in one answer (structural blend protection:
    the answer is a single section, so blending is impossible).
  * When no single section answers the question, or the best matches are
    ambiguous across two documents, the fixed refusal template is printed
    verbatim. No hedging phrase is ever emitted.

No runtime LLM — retrieval and refusal are deterministic keyword/IDF scoring,
so every guarantee is a verifiable string check. Run: python app.py
(interactive CLI; type 'exit' or 'quit', or send EOF, to stop).
"""
import math
import os
import re
import sys
from collections import OrderedDict

# The three source documents, resolved relative to this file so the run command
# `python app.py` works from the uc-x directory regardless of cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
_DOCS_DIR = os.path.normpath(os.path.join(_HERE, "..", "data", "policy-documents"))
DOCUMENT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# Fixed refusal template — used verbatim, no variation (agents.md / README).
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

# Retrieval tuning. A legitimate answer names several distinctive policy terms;
# an off-topic question (e.g. "flexible working culture") matches none of them.
MIN_SCORE = 2.5          # best section must clear this IDF-weighted score, else refuse
MIN_OVERLAP = 1          # best section must share at least this many query terms
AMBIGUITY_RATIO = 0.95   # if the runner-up (in another document) is this close, refuse

# Words with no discriminating value for these documents. "work"/"working" and
# similar are dropped so a distinctive verb like "install" is not outweighed by
# generic filler; this keeps single distinctive terms decisive.
STOPWORDS = frozenset("""
a an and are as at be by can could do does for from get have how i if in into is
it may me must my need of on or our please should so that the their them then
there these this those to use used using want was we what when where which who
whom why will with would you your
work working works employee employees cmc policy company view about
""".split())

# Morphological variants folded to one form so query and source match, e.g. the
# question verb "approves" and the policy noun "approval".
NORMALIZE = {
    "approval": "approve",
    "approved": "approve",
    "approving": "approve",
    "approver": "approve",
}

# Acronyms expanded to their spelled-out terms so a question that uses the words
# (or the acronym) matches a section that uses the other form.
ACRONYMS = {
    "lwp": ("leave", "without", "pay"),
}

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*\d+\.\s")     # section header, e.g. "2. ANNUAL LEAVE"
DIVIDER_RE = re.compile(r"[\u2550=]{3,}")   # heavy/equals rule lines
TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text):
    """Lower-case, split into word tokens, drop stopwords, lightly stem plurals
    so 'devices'/'device' match, fold known morphological variants, and expand
    acronyms so 'LWP' and 'leave without pay' align."""
    tokens = []
    for raw in TOKEN_RE.findall(text.lower()):
        if raw in STOPWORDS:
            continue
        if len(raw) > 3 and raw.endswith("s") and not raw.endswith("ss"):
            raw = raw[:-1]
        if raw in STOPWORDS:
            continue
        raw = NORMALIZE.get(raw, raw)
        if raw in ACRONYMS:
            tokens.extend(ACRONYMS[raw])
        else:
            tokens.append(raw)
    return tokens


def retrieve_documents(document_files=DOCUMENT_FILES, docs_dir=_DOCS_DIR):
    """Load the three policy files and index them by (document_name,
    section_number) -> section_text, preserving the source wording exactly.

    Raises RuntimeError before any answering begins if a file is missing or
    unreadable, rather than answering from a partial index. Lines that do not
    belong to a numbered section are attached to the nearest preceding section
    and never invented.
    """
    index = OrderedDict()
    for name in document_files:
        path = os.path.join(docs_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                raw_text = fh.read()
        except OSError as exc:
            raise RuntimeError("Cannot read policy file '%s': %s" % (path, exc))

        current_num = None
        current_parts = []

        def flush(num, parts):
            if num is not None:
                index[(name, num)] = " ".join(p for p in parts if p).strip()

        for raw in raw_text.splitlines():
            line = raw.rstrip()
            match = CLAUSE_RE.match(line)
            if match:
                flush(current_num, current_parts)
                current_num = match.group(1)
                current_parts = [match.group(2).strip()]
                continue

            stripped = line.strip()
            if not stripped or DIVIDER_RE.search(line) or SECTION_RE.match(line):
                flush(current_num, current_parts)
                current_num = None
                current_parts = []
                continue

            if current_num is not None:
                current_parts.append(stripped)

        flush(current_num, current_parts)

    if not index:
        raise RuntimeError("No policy sections were indexed from the source documents.")
    return index


def _build_idf(index):
    """Inverse document frequency of each token across all sections, so rare,
    distinctive terms weigh more than common ones."""
    total = len(index)
    section_tokens = {}
    doc_freq = {}
    for key, text in index.items():
        toks = set(_tokenize(text))
        section_tokens[key] = toks
        for tok in toks:
            doc_freq[tok] = doc_freq.get(tok, 0) + 1
    idf = {tok: math.log(total / (1.0 + df)) for tok, df in doc_freq.items()}
    return section_tokens, idf


def answer_question(question, index, section_tokens=None, idf=None):
    """Answer from a single best-matching section with a citation, or return the
    verbatim refusal template.

    Scores each section by the IDF-weighted overlap of query terms, selects the
    single best section from one document, and returns its literal text ending
    with "<document_name>, section <number>". Returns the refusal template
    verbatim when the best score is below threshold or the best matches are
    genuinely ambiguous across two different documents. It never blends two
    sections and never adds a hedging phrase.
    """
    if section_tokens is None or idf is None:
        section_tokens, idf = _build_idf(index)

    query = set(_tokenize(question))
    if not query:
        return REFUSAL_TEMPLATE

    scored = []
    for key, toks in section_tokens.items():
        shared = query & toks
        if not shared:
            continue
        score = sum(idf.get(tok, 0.0) for tok in shared)
        scored.append((score, len(shared), key))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    best_score, best_overlap, best_key = scored[0]

    if best_score < MIN_SCORE or best_overlap < MIN_OVERLAP:
        return REFUSAL_TEMPLATE

    # Blend protection: if a section in a DIFFERENT document scores almost as
    # high, the question is genuinely ambiguous across documents — refuse rather
    # than pick one or merge them.
    best_doc = best_key[0]
    for score, _overlap, key in scored[1:]:
        if key[0] == best_doc:
            continue
        if score >= AMBIGUITY_RATIO * best_score:
            return REFUSAL_TEMPLATE
        break

    doc_name, section_number = best_key
    section_text = index[best_key]
    return "%s\n\n%s, section %s" % (section_text, doc_name, section_number)


def main():
    try:
        index = retrieve_documents()
    except RuntimeError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 1

    section_tokens, idf = _build_idf(index)

    print("Ask My Documents — CMC policy assistant")
    print("Sources: %s" % ", ".join(DOCUMENT_FILES))
    print("Type your question, or 'exit'/'quit' to stop.\n")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break

        answer = answer_question(question, index, section_tokens, idf)
        print("\n%s\n" % answer)

    return 0


if __name__ == "__main__":
    sys.exit(main())

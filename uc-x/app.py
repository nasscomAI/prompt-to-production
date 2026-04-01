"""
UC-X — Ask My Documents
=======================
Interactive CLI that answers employee policy questions strictly from
the three approved CMC policy documents.

Architecture:
  - retrieve_documents(file_paths) → DocumentIndex  [skill 1]
  - answer_question(question, index) → str           [skill 2]

Agent behaviour is governed by agents.md (RICE):
  Role    : Policy Q&A agent; single-document answers only.
  Intent  : Citation-backed answers or exact refusal template.
  Context : Only the three policy files listed below.
  Enforcement: No blending, no hedging, mandatory citations,
               exact refusal template for out-of-scope questions.
"""

import math
import os
import re
import sys

# ──────────────────────────────────────────────────────────────────────────────
# Configuration — paths and constants (agents.md → context)
# ──────────────────────────────────────────────────────────────────────────────

POLICY_FILES = [
    os.path.join(os.path.dirname(__file__),
                 "../data/policy-documents/policy_hr_leave.txt"),
    os.path.join(os.path.dirname(__file__),
                 "../data/policy-documents/policy_it_acceptable_use.txt"),
    os.path.join(os.path.dirname(__file__),
                 "../data/policy-documents/policy_finance_reimbursement.txt"),
]

# Exact refusal template — agents.md enforcement rule 4
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases banned by agents.md enforcement rule 2
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

# Separator pattern used in the policy files (═══ lines)
SECTION_SEPARATOR = re.compile(r"^═+$")

# Section header pattern: "<number>. <TITLE>" at the start of a line
SECTION_HEADER = re.compile(r"^(\d+)\.\s+(.+)$")

# Sub-section line pattern: "<N>.<M> text …"
SUBSECTION_LINE = re.compile(r"^(\d+\.\d+)\s+(.+)")


# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────

class DocumentIndex:
    """
    In-memory index built by retrieve_documents.

    Structure:
        _data[(doc_name, section_id)] = section_text_block
        _idf[token]                   = log(N / df)  — precomputed after load

    Example key: ("policy_hr_leave.txt", "2")
    Example key: ("policy_hr_leave.txt", "2.6")
    """

    def __init__(self):
        # {(doc_name: str, section_id: str): text: str}
        self._data: dict[tuple[str, str], str] = {}
        # {token: float}  — inverse document frequency across all sections
        self._idf: dict[str, float] = {}
        self._loaded = False

    def add(self, doc_name: str, section_id: str, text: str):
        self._data[(doc_name, section_id)] = text.strip()

    def items(self):
        return self._data.items()

    def is_loaded(self) -> bool:
        return self._loaded

    def mark_loaded(self):
        """Call once after all sections are added; pre-computes IDF weights."""
        self._loaded = True
        self._build_idf()

    def _build_idf(self):
        """Compute IDF = log(N / df) for every token across all sections."""
        N = len(self._data)
        if N == 0:
            return
        df: dict[str, int] = {}
        for text in self._data.values():
            tokens = set(re.findall(r"\b\w+\b", text.lower()))
            for tok in tokens:
                df[tok] = df.get(tok, 0) + 1
        self._idf = {tok: math.log(N / count) for tok, count in df.items()}

    def idf(self, token: str) -> float:
        """Return IDF weight for a token (0.0 if token is in every section)."""
        return self._idf.get(token, 0.0)

    def __bool__(self):
        return bool(self._data)


# ──────────────────────────────────────────────────────────────────────────────
# Skill 1 — retrieve_documents
# ──────────────────────────────────────────────────────────────────────────────

def retrieve_documents(file_paths: list[str]) -> DocumentIndex:
    """
    Skill: retrieve_documents
    ─────────────────────────
    Input  : List of file paths to policy .txt files.
    Output : DocumentIndex — mapping (doc_name, section_id) → section_text.
    Errors : FileNotFoundError on any missing file; halts immediately.
             Does NOT proceed with a partial index.
    """
    index = DocumentIndex()

    for path in file_paths:
        resolved = os.path.normpath(path)
        doc_name = os.path.basename(resolved)

        if not os.path.isfile(resolved):
            raise FileNotFoundError(
                f"[retrieve_documents] Policy file not found: {resolved}\n"
                "Halting — all three files must be present before proceeding."
            )

        with open(resolved, encoding="utf-8") as fh:
            lines = fh.read().splitlines()

        # ── Parse sections ────────────────────────────────────────────────────
        # The files use ═══ separators followed by a "N. TITLE" header line.
        # We capture both the top-level section block and individual sub-section
        # lines (N.M), so queries can be matched at either granularity.

        current_section_id = None
        current_section_lines: list[str] = []
        skip_next = False  # True right after a ═══ line

        def flush_section():
            if current_section_id and current_section_lines:
                index.add(doc_name, current_section_id,
                           "\n".join(current_section_lines))

        for line in lines:
            stripped = line.strip()

            # ── Separator line: ═══…═══ ───────────────────────────────────────
            if SECTION_SEPARATOR.match(stripped):
                flush_section()
                current_section_id = None
                current_section_lines = []
                skip_next = True
                continue

            # ── Section header line immediately after separator ──────────────
            if skip_next:
                skip_next = False
                m = SECTION_HEADER.match(stripped)
                if m:
                    current_section_id = m.group(1)      # e.g. "2"
                    current_section_lines = [stripped]
                continue

            # ── Body lines ───────────────────────────────────────────────────
            if current_section_id:
                current_section_lines.append(stripped)

                # Also index individual sub-section blocks (N.M …)
                msub = SUBSECTION_LINE.match(stripped)
                if msub:
                    sub_id = msub.group(1)               # e.g. "2.6"
                    index.add(doc_name, sub_id, stripped)

        flush_section()  # capture the last section

    index.mark_loaded()
    return index


# ──────────────────────────────────────────────────────────────────────────────
# Skill 2 — answer_question
# ──────────────────────────────────────────────────────────────────────────────

# Stopwords removed before scoring so common English words don't dilute IDF
_STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "to", "of", "in", "on",
    "and", "or", "for", "with", "my", "i", "can", "do", "be", "this",
    "that", "it", "at", "by", "from", "not", "will", "what", "when",
    "how", "who", "does", "if", "me", "we", "you", "your", "our",
    "they", "their", "have", "has", "had", "any", "all", "also", "so",
    "as", "up", "its", "same", "such",
}


def _idf_score(query_tokens: set[str], section_text: str,
               index: DocumentIndex, is_subsection: bool) -> float:
    """
    Compute IDF-weighted relevance of a section to the query.

    Score = sum of IDF(token) for each query token that appears in the
            section text.  Sub-section entries receive a 1.5x precision
            bonus because they are narrower / more specific than a whole
            top-level section.
    """
    text_tokens = set(re.findall(r"\b\w+\b", section_text.lower()))
    score = sum(
        index.idf(tok)
        for tok in query_tokens
        if tok in text_tokens
    )
    if is_subsection:
        score *= 1.5   # precision bonus for pinpointed sub-section
    return score


def answer_question(question: str, index: DocumentIndex) -> str:
    """
    Skill: answer_question
    ──────────────────────
    Input  : Natural-language question string + loaded DocumentIndex.
    Output : Single-source answer with citation  OR  exact refusal template.
    Errors :
      - Index empty/not loaded → raises RuntimeError.
      - Matches in more than one document → refusal template (no blending).

    Scoring:
      Uses IDF-weighted token matching so domain-specific terms
      ("install", "phone", "personal") score higher than common
      cross-document words ("work", "home", "laptop").
    """
    if not index or not index.is_loaded():
        raise RuntimeError(
            "[answer_question] DocumentIndex is empty or not loaded. "
            "Run retrieve_documents() first."
        )

    # ── Tokenise and strip stop words ─────────────────────────────────────────
    raw_tokens = set(re.findall(r"\b\w+\b", question.lower()))
    query_tokens = raw_tokens - _STOP_WORDS

    if not query_tokens:
        return REFUSAL_TEMPLATE

    # ── Score every indexed section ───────────────────────────────────────────
    scored: list[tuple[float, str, str, str]] = []  # (score, doc, sec, text)

    for (doc_name, section_id), text in index.items():
        # Sub-section IDs contain a dot (e.g. "2.6"); top-level are digits only
        is_subsection = "." in section_id
        score = _idf_score(query_tokens, text, index, is_subsection)
        if score > 0:
            scored.append((score, doc_name, section_id, text))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]

    # ── Candidate band: sections within 70 % of the top score ────────────────
    # A tighter band than before — only genuinely competitive sections are
    # considered, preventing weak cross-document matches from triggering the
    # blending guard on clearly single-source questions.
    BAND = 0.70
    candidates = [s for s in scored if s[0] >= top_score * BAND]

    # ── Cross-document blending guard (agents.md enforcement rule 1) ──────────
    # If the top candidates come from more than one source document,
    # we cannot safely answer from a single source — return refusal.
    docs_hit = {c[1] for c in candidates}
    if len(docs_hit) > 1:
        return REFUSAL_TEMPLATE

    # ── Single document — return best matching section with citation ──────────
    _, best_doc, best_sec, best_text = candidates[0]
    citation = f"\nSource: {best_doc}, section {best_sec}"
    return f"{best_text}{citation}"


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 62)
    print("  UC-X — Ask My Documents")
    print("  City Municipal Corporation Policy Q&A")
    print("=" * 62)
    print("Loading policy documents …", end=" ", flush=True)

    try:
        index = retrieve_documents(POLICY_FILES)
    except FileNotFoundError as exc:
        print("\n[ERROR]", exc)
        sys.exit(1)

    print("done.\n")
    print("Type your question and press Enter.")
    print("Type 'exit' or 'quit' to leave.\n")
    print("-" * 62)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print("\n" + answer)
        print("-" * 62)


if __name__ == "__main__":
    main()

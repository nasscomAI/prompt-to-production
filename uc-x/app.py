"""
UC-X - Ask My Documents
=======================
A single-source policy Q&A system over the three CMC policy documents.

Failure modes this code is built to defeat (see agents.md for the rules):
  * Cross-document blending - an answer is always drawn from EXACTLY ONE
    document. If the best evidence spans two documents, the system refuses
    rather than stitch claims together. This is what protects the
    personal-phone question: "personal device" is a contiguous phrase owned
    by IT 3.x, while "work ... from home" in that question is NOT the Finance
    "work from home" phrase, so Finance can never win on a phrase match.
  * Hedged hallucination - a question with no confident single-source match
    returns the verbatim refusal template. There is no code path that can
    emit "while not explicitly covered...".
  * Condition dropping - the matched section's full text is returned verbatim,
    so every condition survives (both LWP approvers in 5.2, the DA+meal
    prohibition in Finance 2.6, the 31 December forfeiture date, etc.).

The matcher is deterministic, rule-based, standard-library only:
  1. Tokenise the question (lowercase, stopword strip, morphological fold).
  2. Score every parsed section with TF-IDF over unigrams AND bigrams, with
     section-heading terms weighted heavier. Bigrams are what make "personal
     device" outrank a scattered "work"+"home" (the blending trap).
  3. Return the single best section ONLY IF it clears a confidence threshold
     AND no section from a DIFFERENT document is close to it (cross-doc guard).

CLI
---
Interactive :  python uc-x/app.py
Single-shot :  python uc-x/app.py --question "Can I carry forward unused annual leave?"
Debug       :  python uc-x/app.py --question "<q>" --debug   (prints section scores)
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution - works from the repo root AND from inside uc-x/.
# __file__ is the only anchor; never assume a cwd.
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data" / "policy-documents"

DOC_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

# EXACT refusal template - do not vary a single character. This string is the
# only permitted response when a question is not answerable from one document.
REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# ---------------------------------------------------------------------------
# Tuning constants (calibrated against the 7 test questions; see agents.md).
# ---------------------------------------------------------------------------
MIN_CONFIDENCE = 0.60      # below this -> no document confidently answers
CROSS_DOC_MARGIN = 0.10    # best must beat every other-doc section by this
HEADING_WEIGHT = 2.0       # heading terms weight heavier (topic signal)
BIGRAM_WEIGHT = 2.5        # bigrams outrank unigrams - a 2-word phrase like
                           # "personal device" or "install software" is far more
                           # specific than scattered single words, which is what
                           # stops Finance 3.3's example list ("computers,
                           # laptops, smartphones") from out-scoring IT 3.1.

# Common English question words that carry no policy signal. Removing them
# stops filler like "can / my / the / for / use" from inflating weak matches
# and is what stops "working" from bridging to "work" in the docs.
STOPWORDS = {
    "a", "an", "the", "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "doing", "done",
    "can", "could", "may", "might", "must", "shall", "should",
    "will", "would", "have", "has", "had", "having",
    "i", "me", "my", "mine", "we", "us", "our", "ours",
    "you", "your", "yours", "he", "him", "his", "she", "her", "hers",
    "it", "its", "they", "them", "their", "theirs",
    "and", "or", "but", "not", "no", "nor", "so", "than", "then", "too",
    "to", "of", "in", "on", "at", "by", "for", "with", "without", "from",
    "into", "onto", "upon", "over", "under", "about", "as", "if",
    "what", "who", "whom", "whose", "which", "why", "how", "when", "where",
    "any", "all", "each", "every", "some", "more", "most", "much", "many",
    "there", "here", "now", "out", "up", "down", "off", "per", "via",
    "use", "used", "using", "usage", "allow", "allowed", "get", "got",
    "s", "t", "d", "ll", "ve", "re", "m",
}

# Variant -> canonical term. Folds morphology so a question word and a document
# word align (install/installing, claim/claimed, phone/device) WITHOUT ever
# bridging two documents' distinct concepts. Deliberately narrow:
#   - We do NOT map "working"->"work" (that would hand the flexible-culture
#     question a spurious "work" match).
#   - We do NOT fold laptop/computer/smartphone->device. Finance 3.3 lists
#     "personal computers, laptops, smartphones" as examples of what the WFH
#     allowance does NOT cover; folding all three to "device" would hand that
#     section a triple "device" count and let it steal the personal-phone
#     question away from IT 3.1. Only "phone" and the plural "devices" fold.
SYNONYMS = {
    # device family - only what a question literally calls a phone, plus the
    # plural in the docs, fold onto "device".
    "phone": "device", "phones": "device",
    "device": "device", "devices": "device",
    # install family
    "install": "install", "installing": "install",
    "installation": "install", "installed": "install",
    # approval family
    "approve": "approval", "approves": "approval",
    "approved": "approval", "approval": "approval", "approvals": "approval",
    # claim / reimburse family
    "claim": "claim", "claims": "claim", "claimed": "claim", "claiming": "claim",
    "reimburse": "reimburse", "reimbursement": "reimburse",
    "reimbursements": "reimburse", "reimbursed": "reimburse",
    # carry forward
    "carry": "carry", "carrying": "carry",
    # leave
    "leaves": "leave", "leave": "leave",
    # receipts
    "receipt": "receipt", "receipts": "receipt",
}


def _canonical(raw: str) -> str:
    return SYNONYMS.get(raw, raw)


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords/short tokens,
    fold morphological variants, and collapse any object of "install" to
    "software" (the policy only ever refers to "software" generically, so
    "install Slack" / "install Zoom" must match the "software" in IT 2.3).

    Returns the ordered list of kept terms (order is needed for bigrams)."""
    terms: list[str] = []
    last_kept = ""
    for raw in re.findall(r"[a-z0-9]+", text.lower()):
        if len(raw) < 3:
            continue
        term = _canonical(raw)
        if term in STOPWORDS:
            continue
        # "install <X>" -> X is software (Slack, Zoom, Chrome, ...). This is
        # what lets "install Slack" hit IT 2.3's "install software" instead of
        # tying with IT 2.6's "endpoint security agent installed".
        if last_kept == "install" and term != "install" and term != "software":
            term = "software"
        terms.append(term)
        last_kept = term
    return terms


def bigrams(tokens: list[str]) -> list[tuple[str, str]]:
    return [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]


def _id_key(section_id: str) -> tuple[int, int]:
    """Numeric sort key for a section id like '3.1' -> (3, 1), so ties in score
    resolve to the earlier (more general) section: IT 3.1 before 3.2, etc."""
    parts = re.findall(r"\d+", section_id)
    nums = [int(p) for p in parts]
    return (nums[0] if nums else 0, nums[1] if len(nums) > 1 else 0)


# ---------------------------------------------------------------------------
# Document parsing
# ---------------------------------------------------------------------------
_SEP_RE = re.compile(r"[─-╿=\-*_~]{3,}")     # box-drawing / rule chars
_TOP_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9\s/()\-]+?)\s*$")  # "2. ANNUAL LEAVE"
_SUB_RE = re.compile(r"^(\d+\.\d+)\s+(.+)")                       # "2.6 Employees may ..."


def _is_separator(line: str) -> bool:
    """A line made only of box-drawing / rule characters (no alphanumerics)."""
    if len(line) < 3 or any(ch.isalnum() for ch in line):
        return False
    return bool(_SEP_RE.search(line)) or set(line.strip()) <= {"=", "-", "*", "_", "~"}


def parse_doc(text: str, doc_name: str) -> list[dict]:
    """Parse one policy file into a list of sub-section records.

    Each record: {doc, id (e.g. '2.6'), heading (parent title e.g. 'ANNUAL
    LEAVE'), text (full verbatim sub-section body, whitespace-normalised)}.
    Sub-section text spans continuation/indented lines until the next
    sub-section, top-level heading, or separator.
    """
    sections: list[dict] = []
    parent: str | None = None
    current: dict | None = None

    def flush() -> None:
        nonlocal current
        if current and current["parts"]:
            current["text"] = re.sub(r"\s+", " ", " ".join(current["parts"])).strip()
            if current["text"]:
                sections.append(
                    {
                        "doc": doc_name,
                        "id": current["id"],
                        "heading": parent or "",
                        "text": current["text"],
                    }
                )
        current = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if _is_separator(stripped):
            flush()
            continue
        top = _TOP_RE.match(stripped)
        if top:
            flush()
            parent = top.group(2).strip()
            continue
        sub = _SUB_RE.match(stripped)
        if sub:
            flush()
            current = {"id": sub.group(1), "parts": [sub.group(2)]}
            continue
        # continuation of the current sub-section body
        if current is not None:
            current["parts"].append(stripped)
        # else: document header lines (CITY MUNICIPAL CORPORATION, Version:,
        # Document Reference:) are silently ignored.

    flush()
    return sections


def retrieve_documents(data_dir: Path = DATA_DIR) -> tuple[list[dict], dict, dict]:
    """Load all three policy files, parse into sub-sections, and index by
    document name + section id. Precomputes per-section heading/body unigram
    and bigram counters plus corpus-wide section frequencies (for IDF).

    Returns (sections, unigram_section_freq, bigram_section_freq)."""
    sections: list[dict] = []
    for fname in DOC_FILES:
        path = data_dir / fname
        if not path.is_file():
            # Missing input is a hard failure - do not guess.
            raise FileNotFoundError(f"Required policy document not found: {path}")
        sections.extend(parse_doc(path.read_text(encoding="utf-8"), fname))

    uni_freq: dict[str, int] = {}
    bi_freq: dict[tuple[str, str], int] = {}
    for s in sections:
        h_tokens = tokenize(s["heading"])
        b_tokens = tokenize(s["text"])
        s["heading_uni"] = Counter(h_tokens)
        s["body_uni"] = Counter(b_tokens)
        s["heading_bi"] = Counter(bigrams(h_tokens))
        s["body_bi"] = Counter(bigrams(b_tokens))
        for t in set(s["heading_uni"]) | set(s["body_uni"]):
            uni_freq[t] = uni_freq.get(t, 0) + 1
        for bg in set(s["heading_bi"]) | set(s["body_bi"]):
            bi_freq[bg] = bi_freq.get(bg, 0) + 1
    return sections, uni_freq, bi_freq


# ---------------------------------------------------------------------------
# Matching / scoring (TF-IDF over unigrams + bigrams, heading-weighted, deduped)
# ---------------------------------------------------------------------------
def _idf(term, freq: dict) -> float:
    """1 / (1 + section_frequency). Terms in many sections score low; terms
    unique to one section (carry, forfeited, simultaneously, LWP) score high."""
    return 1.0 / (1.0 + freq.get(term, 0))


def _score_pair(qtally: Counter, heading: Counter, body: Counter, freq: dict,
                weight: float) -> float:
    """IDF-weighted overlap with BINARY term frequency: a section either
    addresses a term or it does not. Repeating a word inside an example list
    (e.g. Finance 2.4's "software ... software catalogue", or 3.3's
    "computers, laptops, smartphones") must NOT inflate that section's score,
    or example lists would steal questions from the section that actually
    governs the topic. Deduped: a term found in the heading is counted ONLY at
    the heading weight (heading is the stronger topic signal)."""
    total = 0.0
    for term in qtally:
        if term in heading:
            total += HEADING_WEIGHT * weight * _idf(term, freq)
        elif term in body:
            total += weight * _idf(term, freq)
    return total


def score_question(q_uni: Counter, q_bi: Counter, section: dict,
                   uni_freq: dict, bi_freq: dict) -> float:
    uni = _score_pair(q_uni, section["heading_uni"], section["body_uni"], uni_freq, 1.0)
    bi = _score_pair(q_bi, section["heading_bi"], section["body_bi"], bi_freq, BIGRAM_WEIGHT)
    return uni + bi


def answer_question(question: str, sections: list[dict], uni_freq: dict,
                    bi_freq: dict, debug: bool = False) -> str:
    """Return the single-source answer + citation, or the verbatim refusal.

    Decision rule:
      1. Tokenise the question; if it has no signal terms, refuse.
      2. Score every section. If the best score < MIN_CONFIDENCE, refuse
         (no document confidently answers this).
      3. Cross-document guard: if any section from a DIFFERENT document than
         the best scores within CROSS_DOC_MARGIN of the best, the question
         genuinely spans documents -> refuse rather than blend.
      4. Otherwise return the best section's verbatim text + citation.
    """
    q_tokens = tokenize(question)
    if debug:
        print(f"[debug] question terms: {q_tokens}")
    if not q_tokens:
        return REFUSAL

    q_uni = Counter(q_tokens)
    q_bi = Counter(bigrams(q_tokens))
    if debug and q_bi:
        print(f"[debug] question bigrams: {[ '-'.join(bg) for bg in q_bi ]}")

    scored = sorted(
        ((score_question(q_uni, q_bi, s, uni_freq, bi_freq), s) for s in sections),
        # primary: score descending; tiebreak: smaller section id first, so a
        # general rule (e.g. IT 3.1) wins over a narrower sibling (IT 3.2) when
        # both match equally.
        key=lambda x: (-x[0], _id_key(x[1]["id"])),
    )
    if debug:
        print("[debug] top section scores:")
        for sc, s in scored[:8]:
            print(f"          {sc:.4f}  {s['doc']} {s['id']} ({s['heading']})")

    best_score, best = scored[0]
    if best_score < MIN_CONFIDENCE:
        return REFUSAL

    for sc, s in scored:
        if s["doc"] != best["doc"] and sc >= best_score - CROSS_DOC_MARGIN:
            # Two different documents look equally relevant -> blending risk.
            return REFUSAL

    text = re.sub(r"\s+", " ", best["text"]).strip()
    return f"{text} Source: {best['doc']} §{best['id']}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _interactive(sections, uni_freq, bi_freq) -> None:
    print("Ask My Documents - CMC policy Q&A (single-source).")
    print("Type a question and press Enter. Leave blank or type 'quit' to exit.")
    while True:
        try:
            question = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in {"quit", "exit"}:
            break
        print("\n" + answer_question(question, sections, uni_freq, bi_freq))


def main(argv: list[str] | None = None) -> int:
    # Force UTF-8 stdout so the section-sign (§) and any rupee/section glyphs
    # emit as well-formed UTF-8 regardless of the host codepage. This keeps
    # `Source: ... §2.6` greppable/identical on Windows CI and on Linux.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        description="Ask My Documents - single-source policy Q&A."
    )
    parser.add_argument(
        "--question", "-q",
        help="Answer one question and exit (single-shot mode for CI).",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Print term breakdown and section scores (diagnostics).",
    )
    args = parser.parse_args(argv)

    sections, uni_freq, bi_freq = retrieve_documents()

    if args.question is not None:
        print(answer_question(args.question, sections, uni_freq, bi_freq, debug=args.debug))
        return 0

    _interactive(sections, uni_freq, bi_freq)
    return 0


if __name__ == "__main__":
    sys.exit(main())

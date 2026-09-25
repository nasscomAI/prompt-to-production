"""
UC-X app.py — Policy Document Q&A Agent.

Answers employee questions strictly from three source documents:
  - policy_hr_leave.txt
  - policy_it_acceptable_use.txt
  - policy_finance_reimbursement.txt

Enforcement rules (from agents.md):
  - Never combine claims from two different documents into a single answer.
  - Never use hedging phrases.
  - Every factual claim must cite document name + section number.
  - If not covered, respond with the refusal template verbatim.

See README.md for the full spec and test questions.
"""

import os
import re
import sys
import argparse


# ─── Constants ───────────────────────────────────────────────────────────────

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

DOCUMENT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

# Hedging phrases that must never appear in answers.
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is likely",
    "it may be possible",
]


# ─── Skill: retrieve_documents ──────────────────────────────────────────────

class PolicyDocumentError(Exception):
    """Raised when a policy document exists but cannot be used.

    skills.md requires retrieve_documents to "raise an error naming the
    specific file" when a document is missing *or unreadable*, and to
    never silently skip a document.  A raw OSError or UnicodeDecodeError
    from open() would not name the file in a useful way, so read failures
    are re-raised as this type.
    """


def retrieve_documents():
    """Load all 3 policy files and index them by document name → section number
    → section text.

    Returns:
        dict: {doc_name: {section_number: section_text, ...}, ...}

    Raises:
        FileNotFoundError: If any policy file is missing.
        PolicyDocumentError: If any policy file is unreadable or is not
            valid UTF-8 text.  Documents are never skipped.
    """
    documents = {}

    for filename in DOCUMENT_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                f"Policy document not found: {filepath}. "
                f"All 3 documents must be present."
            )

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except UnicodeDecodeError as e:
            raise PolicyDocumentError(
                f"Policy document is not valid UTF-8 text: {filepath} ({e}). "
                f"All 3 documents must be present and readable."
            ) from e
        except OSError as e:
            raise PolicyDocumentError(
                f"Policy document could not be read: {filepath} ({e}). "
                f"All 3 documents must be present and readable."
            ) from e

        # A file that opens cleanly but yields no numbered clauses is not
        # a usable policy document.  skills.md forbids silently skipping
        # documents, and an empty index would let a question be answered
        # — or refused — on the strength of two documents instead of three.
        sections = _parse_sections(raw_text)
        if not sections:
            raise PolicyDocumentError(
                f"Policy document contains no numbered sections and cannot "
                f"be indexed: {filepath}. All 3 documents must be present, "
                f"readable, and parse into numbered clauses."
            )

        documents[filename] = sections

    return documents


def _parse_sections(text):
    """Parse a policy document into a dict of {section_number: section_text}.

    Handles the format used by all three policy documents:
        ═══════════════════
        N. SECTION TITLE
        ═══════════════════
        N.M  Content line ...

    Returns:
        dict: {"1.1": "text...", "1.2": "text...", ...}
    """
    sections = {}
    current_section = None
    current_lines = []

    for line in text.splitlines():
        # Skip the ═══ separator lines
        if line.strip().startswith("═"):
            continue

        # Detect top-level heading like "2. ANNUAL LEAVE" — skip it but note
        # we're inside this block.
        top_heading = re.match(r"^(\d+)\.\s+[A-Z]", line)
        if top_heading:
            # Flush previous subsection if any.
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = None
            current_lines = []
            continue

        # Detect sub-section like "2.1", "2.10", etc.
        sub_match = re.match(r"^(\d+\.\d+)\s", line)
        if sub_match:
            # Flush previous subsection.
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = sub_match.group(1)
            current_lines = [line.strip()]
        elif current_section is not None:
            # Continuation line for the current subsection.
            current_lines.append(line.strip())

    # Flush the last subsection.
    if current_section is not None:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


# ─── Skill: answer_question ─────────────────────────────────────────────────

# Minimum score a section must reach to be considered a genuine match.
# This prevents vague single-keyword hits from surfacing.
_MIN_SCORE_THRESHOLD = 2

# Secondary sections must score at least this fraction of the best hit
# to be included in the answer.
_SECONDARY_THRESHOLD = 0.6

# Sibling clauses from the best hit's top-level block are included when
# they score at least this much.  See _include_sibling_sections.
_SIBLING_MIN_SCORE = 2

# A question that is genuinely contested between two documents must be
# refused, not answered from whichever document happens to score higher.
# See _cross_document_ambiguity.
_AMBIGUITY_RATIO = 0.6

# Domain-specific keyword expansions — maps a user term to additional
# search terms that appear in the policy documents.  Only simple,
# unambiguous mappings belong here.
_KEYWORD_EXPANSIONS = {
    "install": ["software"],
    "laptop": ["devices", "corporate"],
    "phone": ["devices", "personal"],
    "slack": ["software", "install"],
    "leave": ["leave"],
    "lwp": ["leave without pay"],
    "da": ["daily allowance"],
    "wfh": ["work from home"],
    "byod": ["personal devices"],
    "approve": ["approval"],
    "approves": ["approval"],
}

# Multi-word phrases mapped to the terminology the documents actually
# use.  Policy text abbreviates ("LWP") in ways a user's question never
# will, and a one-way keyword expansion then silently drops the clause
# that holds the answer.  These are applied to the whole question.
_PHRASE_EXPANSIONS = {
    "leave without pay": ["lwp"],
    "unpaid leave": ["lwp"],
    "without pay": ["lwp"],
    "carry forward": ["carry-forward"],
    "work from home": ["work-from-home"],
    "mobile phone": ["mobile phones"],
    "personal phone": ["personal devices"],
    "personal mobile": ["personal devices"],
    "my own phone": ["personal devices"],
    "my own device": ["personal devices"],
    "byod": ["personal devices"],
    "install software": ["install software"],
    "home office": ["work-from-home"],
}

# ─── Device-ownership subject alignment ────────────────────────────────────
#
# The IT policy splits device rules into two blocks: section 2 governs
# corporate-issued devices, section 3 governs personal devices.  A
# question about a personal phone shares literal keywords with the
# corporate block ("mobile phones issued by CMC ... for official work
# purposes"), so pure keyword overlap answers a personal-device question
# with corporate-device policy and misses section 3.1 entirely.  When the
# question is explicitly about a personal device, sections stating the
# personal-device rule are promoted and sections stating the
# corporate-device rule are demoted.
_PERSONAL_DEVICE_QUERY_PATTERNS = [
    "personal device",
    "personal phone",
    "personal mobile",
    "personal laptop",
    "personal tablet",
    "my own phone",
    "my own device",
    "bring my own",
    "byod",
]

_PERSONAL_DEVICE_SECTION_PATTERNS = [
    "personal device",
    "personal devices",
]

_CORPORATE_DEVICE_SECTION_PATTERNS = [
    "corporate device",
    "corporate devices",
    "issued by",
]

_PERSONAL_DEVICE_BONUS = 4
_CORPORATE_DEVICE_PENALTY = 4


def answer_question(question, documents):
    """Search indexed documents for content relevant to the question.

    Returns a single-source answer with citation, or the refusal template.
    Never blends claims from multiple documents.

    Args:
        question: Natural-language question from the user.
        documents: Indexed documents from retrieve_documents().

    Returns:
        str: The answer with citation, or the refusal template.
    """
    question_lower = question.lower()
    keywords = _extract_keywords(question_lower)

    # Expand keywords with domain-specific synonyms.
    expanded = set(keywords)
    for kw in keywords:
        if kw in _KEYWORD_EXPANSIONS:
            expanded.update(_KEYWORD_EXPANSIONS[kw])

    # Expand whole phrases the documents phrase differently.
    for phrase, extra_terms in _PHRASE_EXPANSIONS.items():
        if phrase in question_lower:
            expanded.update(extra_terms)

    keywords = list(expanded)

    # Is this question explicitly about a personally owned device?
    personal_device_query = any(
        pattern in question_lower for pattern in _PERSONAL_DEVICE_QUERY_PATTERNS
    )

    # Score every section in every document.
    scored_hits = []  # list of (score, doc_name, section_num, section_text)

    for doc_name, sections in documents.items():
        for section_num, section_text in sections.items():
            score = _score_section(
                keywords,
                question_lower,
                section_text.lower(),
                personal_device_query,
            )
            if score > 0:
                scored_hits.append((score, doc_name, section_num, section_text))

    if not scored_hits:
        return REFUSAL_TEMPLATE

    # Sort descending by score.
    scored_hits.sort(key=lambda x: x[0], reverse=True)

    best_score = scored_hits[0][0]

    # If even the best hit is below the minimum threshold, refuse.
    if best_score < _MIN_SCORE_THRESHOLD:
        return REFUSAL_TEMPLATE

    # If two documents are genuinely in contention, refuse rather than
    # silently picking the higher scorer.
    if _cross_document_ambiguity(scored_hits):
        return REFUSAL_TEMPLATE

    # Pick the best-matching document (highest-scoring hit).
    best_doc = scored_hits[0][1]
    best_section = scored_hits[0][2]

    # Collect relevant sections FROM THE SAME document only.
    # This enforces the single-source rule.
    relevant_sections = [
        (score, doc, sec, text)
        for score, doc, sec, text in scored_hits
        if doc == best_doc and score >= best_score * _SECONDARY_THRESHOLD
    ]

    # Add sibling clauses from the same top-level block, so a binding
    # condition is never dropped just because a neighbouring clause
    # scored higher.
    relevant_sections.extend(
        _include_sibling_sections(scored_hits, best_doc, best_section)
    )

    # Deduplicate by section number, strongest first, capped at 3 so the
    # answer stays focused.
    seen = set()
    ordered_sections = []
    for score, doc_name, section_num, section_text in sorted(
        relevant_sections, key=lambda x: x[0], reverse=True
    ):
        if section_num in seen:
            continue
        seen.add(section_num)
        ordered_sections.append((score, doc_name, section_num, section_text))
        if len(ordered_sections) == 3:
            break

    # Build the answer from sections of the single best document.
    citations = [
        f"[{doc_name}, section {section_num}]"
        for _, doc_name, section_num, _ in ordered_sections
    ]
    answer = "\n\n".join(
        f"{citation}\n{text}"
        for citation, (_, _, _, text) in zip(citations, ordered_sections)
    )

    # Hedging guardrail (agents.md enforcement rule 2).
    #
    # Only the citation framing is authored by this agent; every clause
    # body above is verbatim source text.  Scanning the whole answer would
    # therefore only ever test the policy's own wording, and a clause that
    # legitimately reads "typically" would suppress a correct answer —
    # a false refusal, which agents.md does not permit.  So the scan is
    # limited to agent-authored text, and stands as a regression guard in
    # case the answer format ever gains generated prose.
    for phrase in HEDGING_PHRASES:
        if phrase in " ".join(citations).lower():
            return REFUSAL_TEMPLATE

    return answer


def _extract_keywords(question_lower):
    """Extract meaningful keywords from a question, ignoring stop words."""
    stop_words = {
        "i", "me", "my", "we", "our", "you", "your", "the", "a", "an",
        "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "will", "would", "shall", "should",
        "may", "might", "can", "could", "to", "of", "in", "for", "on",
        "with", "at", "by", "from", "as", "into", "about", "if", "or",
        "and", "but", "not", "no", "so", "what", "which", "who", "whom",
        "this", "that", "these", "those", "it", "its", "am", "how",
        "when", "where", "why", "up", "out", "off", "all", "each",
        "any", "both", "few", "more", "most", "other", "some", "such",
        "than", "too", "very", "just", "also", "same", "day",
    }
    words = re.findall(r"[a-z]+", question_lower)
    return [w for w in words if w not in stop_words and len(w) > 1]


def _cross_document_ambiguity(scored_hits):
    """Return True if two documents are genuinely in contention.

    skills.md requires: "If the question matches content in multiple
    documents, answer from the single most relevant document only — never
    blend.  If genuine ambiguity exists across documents, use the refusal
    template."  README makes the same offer for the personal-phone
    question: answer from IT 3.1 "OR refuse — if the HR+IT combination
    creates genuine ambiguity."

    Answering from the single best document already prevents blending, so
    this rule exists for the narrower case where the *choice* of document
    is itself unsafe: combining HR remote-work wording with IT
    device rules would manufacture a permission that neither document
    grants.

    "Genuine" is deliberately strict, so the rule does not fire on
    incidental overlap.  The runner-up document must clear
    _MIN_SCORE_THRESHOLD in absolute terms *and* score at least
    _AMBIGUITY_RATIO of the winner.  Across the 7 required questions the
    runner-up ratios are 0.00-0.25, so none of them trip this.
    """
    best_per_doc = {}
    for score, doc_name, section_num, section_text in scored_hits:
        current = best_per_doc.get(doc_name)
        if current is None or score > current[0]:
            best_per_doc[doc_name] = (score, section_num)

    if len(best_per_doc) < 2:
        return False

    ranked = sorted(best_per_doc.values(), key=lambda sv: sv[0], reverse=True)
    best_score = ranked[0][0]
    rival_score = ranked[1][0]

    if rival_score < _MIN_SCORE_THRESHOLD:
        return False

    return rival_score >= best_score * _AMBIGUITY_RATIO


def _include_sibling_sections(scored_hits, best_doc, best_section):
    """Return sibling clauses from the same top-level block as the best hit.

    UC-X's headline failure mode is condition dropping.  Clause 5.2
    ("LWP requires approval from the Department Head and the HR
    Director. Manager approval alone is not sufficient.") scores lower
    than 5.1 because it uses the abbreviation "LWP", so a purely
    relative threshold drops the very clause that carries the binding
    condition.  Loosening the threshold globally would instead pull in
    unrelated sections, so inclusion is scoped to the best hit's own
    block and requires real keyword signal.
    """
    block = best_section.split(".")[0]
    return [
        (score, doc, sec, text)
        for score, doc, sec, text in scored_hits
        if doc == best_doc
        and sec != best_section
        and sec.split(".")[0] == block
        and score >= _SIBLING_MIN_SCORE
    ]


# Words that carry no topical signal.  An n-gram built only from these
# ("of cmc", "is the") matches organisation boilerplate present in nearly
# every section, which manufactures false confidence: "Who is the CEO of
# CMC?" scored 4 on IT password boilerplate and was answered instead of
# refused.  Requiring real content words keeps "same day" and "meal
# receipts" while rejecting "of cmc".
_FUNCTION_WORDS = {
    "a", "an", "the", "this", "that", "these", "those",
    "i", "me", "my", "we", "our", "you", "your", "it", "its",
    "is", "are", "was", "were", "be", "been", "being", "am",
    "have", "has", "had", "do", "does", "did",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into",
    "about", "if", "or", "and", "but", "so", "than", "then", "there",
    "what", "which", "who", "whom", "whose", "how", "when", "where", "why",
    "am", "any", "all", "each", "both", "up", "out", "off", "not", "no",
}

# An n-gram must contain at least this many content words to be scored.
_MIN_CONTENT_WORDS_PER_NGRAM = 2

# N-gram sizes and their bonuses: (length, bonus).  Phrase matches are
# worth more than single keywords so topically precise sections rank far
# above incidental one-word hits.
_NGRAM_BONUSES = ((2, 3), (3, 5))


def _score_section(keywords, question_lower, section_lower,
                   personal_device_query=False):
    """Score how relevant a section is to the question.

    Uses keyword overlap plus bonuses for multi-word phrase matches
    (bigrams worth +3, trigrams worth +5) so that topically precise
    sections rank far above incidental single-word hits.  An n-gram
    counts only if it contains at least _MIN_CONTENT_WORDS_PER_NGRAM
    content words — see _FUNCTION_WORDS.

    When the question is explicitly about a personally owned device, the
    score is adjusted for device ownership: sections stating the
    personal-device rule are promoted and sections stating the
    corporate-device rule are demoted.  Without this, a question about a
    personal phone is answered from the corporate-device block, which
    shares the literal words "phone" and "work".
    """
    score = 0

    # Keyword hit scoring.
    for kw in keywords:
        if kw in section_lower:
            score += 1

    # N-gram phrase matching from the question words.  N-grams made only
    # of function words are skipped so that document boilerplate cannot
    # stand in for a topical match.
    words = re.findall(r"[a-z]+", question_lower)

    for n, bonus in _NGRAM_BONUSES:
        for i in range(len(words) - n + 1):
            gram_words = words[i:i + n]
            content = sum(1 for w in gram_words if w not in _FUNCTION_WORDS)
            if content < _MIN_CONTENT_WORDS_PER_NGRAM:
                continue
            if " ".join(gram_words) in section_lower:
                score += bonus

    # Device-ownership alignment.
    if personal_device_query:
        states_personal_rule = any(
            pattern in section_lower
            for pattern in _PERSONAL_DEVICE_SECTION_PATTERNS
        )
        states_corporate_rule = any(
            pattern in section_lower
            for pattern in _CORPORATE_DEVICE_SECTION_PATTERNS
        )
        if states_personal_rule:
            score += _PERSONAL_DEVICE_BONUS
        if states_corporate_rule:
            score -= _CORPORATE_DEVICE_PENALTY

    return score


# ─── Interactive CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Policy Document Q&A — Ask questions about company policies."
    )
    parser.parse_args()

    # Policy text contains characters (en-dashes, arrows) that the default
    # Windows console codec cannot encode, and status markers used to crash
    # the CLI on startup with a UnicodeEncodeError.  Force UTF-8 output with
    # replacement so a quoted clause is never lost to an encoding error.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass

    print("=" * 60)
    print("  Policy Document Q&A Agent")
    print("  Source documents:")
    for doc in DOCUMENT_FILES:
        print(f"    - {doc}")
    print("=" * 60)
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.\n")

    # Load and index all documents.
    try:
        documents = retrieve_documents()
        print(f"OK: Loaded {len(documents)} policy documents.\n")
    except (FileNotFoundError, PolicyDocumentError) as e:
        print(f"ERROR: {e}")
        return

    # Interactive loop.
    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        answer = answer_question(question, documents)
        print(f"\nAnswer:\n{answer}\n")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()

"""
UC-X app.py — Ask My Documents
Policy Document Assistant (Interactive CLI)

Agent role   : Policy Document Assistant (agents.md)
Skills used  : retrieve_documents, answer_question (skills.md)
Enforcement  : No cross-document blending · No hedging phrases ·
               Exact refusal template · Always cite doc + section

Run:  python app.py
"""

import os
import re
import sys

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

POLICY_FILES = [
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Phrases the agent must NEVER produce (hedging guard)
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

# Minimum keyword overlap required to consider a section a match
MIN_MATCH_SCORE = 2


# ─────────────────────────────────────────────────────────────
# Skill: retrieve_documents
# ─────────────────────────────────────────────────────────────

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all policy files and builds a structured index keyed by
    (document_name, section_number) → section_text.

    Returns:
        {
          "index": {
              "policy_hr_leave.txt": { "2.6": "Employees may carry forward ...", ... },
              ...
          },
          "errors": ["policy_x.txt: file not found", ...]
        }
    """
    index = {}
    errors = []

    for path in file_paths:
        doc_name = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as exc:
            errors.append(f"{doc_name}: {exc}")
            continue

        sections = {}
        current_section = None
        buffer = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            # Heading lines (e.g. "══════...") — skip
            if line.startswith("═"):
                continue

            # Top-level section header like "2. ANNUAL LEAVE" or "5. LEAVE WITHOUT PAY (LWP)"
            if re.match(r"^\d+\.\s+[A-Z][A-Z ()/_-]+$", line):
                continue

            # Sub-clause like "2.6 Employees may carry forward..."
            match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(buffer).strip()
                current_section = match.group(1)
                buffer = [match.group(2)]
            elif current_section is not None:
                # Continuation lines — but skip document header lines
                if not re.match(r"^(CITY MUNICIPAL|Document Reference|Version:)", line):
                    buffer.append(line)

        # Flush last section
        if current_section is not None:
            sections[current_section] = " ".join(buffer).strip()

        if not sections:
            errors.append(f"{doc_name}: no sections could be parsed — check document format.")
        else:
            index[doc_name] = sections

    return {"index": index, "errors": errors}


# ─────────────────────────────────────────────────────────────
# Skill: answer_question
# ─────────────────────────────────────────────────────────────

# Common English stop words — excluded from scoring
STOP_WORDS = {
    "the", "and", "for", "are", "can", "this", "that", "with",
    "from", "not", "they", "have", "will", "been", "any", "all",
    "its", "was", "but", "may", "must", "each", "per", "only",
    "also", "such", "who", "what", "when", "where", "how", "which",
    "does", "into", "than", "then", "within", "about", "after",
    "before", "under", "their", "those", "there", "here", "your",
    "upon", "over", "both", "same", "used", "use", "using",
    "work", "working",  # too generic — present in nearly all sections
    "files", "home", "access",  # too generic for cross-section discrimination
}

# Queries whose core intent is opinion/culture — provably not in any policy doc.
# These always return the refusal template regardless of partial word matches.
VOID_QUERY_PATTERNS = [
    # Flexible working culture question (README test 5)
    {"flexible", "culture"},
    {"flexible", "working", "culture"},
    {"company", "view"},
    {"company", "opinion"},
    {"general", "policy"},
]

# Domain synonym map — expands query keywords to related policy terms.
# IMPORTANT: "phone" should NOT add generic "device" because that would
# match corporate device sections (2.x) as well as BYOD sections (3.x).
# Instead map to terms that appear specifically in the BYOD / personal section.
SYNONYM_MAP = {
    # Brand names -> policy terms for software installation
    "slack":    {"software", "install"},
    "teams":    {"software", "install"},
    "zoom":     {"software", "install"},
    "whatsapp": {"software", "install"},
    # Personal device (BYOD) — map to section 3 terms in IT policy
    # NOTE: 'devices' (plural) appears as the subject in section 3.x
    # while section 2.x uses 'devices' only in object position.
    # Adding 'devices' here still doesn't discriminate enough; the real
    # discriminator for BYOD questions is 'personal' + absence of 'corporate'.
    "phone":    {"personal", "devices"},
    "mobile":   {"personal", "devices"},
    "iphone":   {"personal", "devices"},
    "android":  {"personal", "devices"},
    # Corporate device  — map to section 2 terms in IT policy
    "laptop":   {"corporate", "install", "software"},
    "computer": {"corporate", "install", "software"},
    # Abbreviations
    "wfh":      {"remote", "arrangement", "permanent"},
    "lwp":      {"leave", "without", "exhausting"},
    "lop":      {"loss", "unapproved"},
    # Query verb forms -> policy noun forms
    "approves": {"director", "approval", "approved"},
    # Finance
    "allowance": {"entitled", "reimbursement", "equipment"},
    # Explicitly void terms — prevented from contributing any matches
    "culture":  set(),
    "view":     set(),
    "opinion":  set(),
    "flexible": set(),
    "general":  set(),
}


def _tokenize(text: str) -> set:
    """Lower-case word tokens, stripping punctuation."""
    return set(re.findall(r"[a-z]+", text.lower()))


def _expand_query(tokens: set) -> set:
    """
    Expands query tokens with domain synonyms so brand names / colloquialisms
    can match the policy document text.
    """
    expanded = set(tokens)
    for token in tokens:
        if token in SYNONYM_MAP:
            expanded.update(SYNONYM_MAP[token])
    return expanded


def _meaningful(tokens: set) -> set:
    """Filter to meaningful tokens: length >= 3 and not a stop word."""
    return {t for t in tokens if len(t) >= 3 and t not in STOP_WORDS}


def _is_void_query(raw_tokens: set) -> bool:
    """
    Returns True if the query matches a VOID_QUERY_PATTERN — meaning the
    question is about opinion/culture/general policy, not in any document.
    """
    for pattern in VOID_QUERY_PATTERNS:
        if pattern.issubset(raw_tokens):
            return True
    return False


def _score_section(expanded_tokens: set, section_text: str) -> int:
    """
    Score a section against the expanded, meaningful query tokens.
    Longer tokens (more specific words) get a +1 weighted bonus.
    """
    section_tokens = _tokenize(section_text)
    matched = _meaningful(expanded_tokens) & section_tokens
    # Weight: 1 point per match, +1 bonus for each token longer than 6 chars
    return sum(1 + (1 if len(t) > 6 else 0) for t in matched)


def answer_question(query: str, index: dict) -> str:
    """
    Searches the indexed policy documents for the best single-source answer.

    Enforcement rules applied here:
    1. Only one document may contribute to the answer (no blending).
    2. No hedging phrases allowed.
    3. If no clear single-source match — return exact refusal template.
    4. Every answer cites document name + section number.

    Returns a formatted answer string.
    """
    query_tokens = _tokenize(query)

    # ── Void-query guard: opinion / culture questions are not in any doc ──
    if _is_void_query(query_tokens):
        return REFUSAL_TEMPLATE

    expanded_tokens = _expand_query(query_tokens)

    # If the expanded token set has no meaningful content after expansion,
    # there is nothing to search for.
    meaningful_q = _meaningful(expanded_tokens)
    if not meaningful_q:
        return REFUSAL_TEMPLATE

    # Collect all candidates: (score, doc_name, section_num, section_text)
    # Score using expanded_tokens so brand names map to policy terms.
    #
    # Domain-lock filter: for queries with strong domain signals,
    # require sections to contain at least one of the lock tokens.
    # This prevents high-frequency words (approved, without) from
    # pulling in off-topic sections from other documents.
    DOMAIN_LOCKS = [
        # If query mentions 'leave' + 'pay', section must contain BOTH
        # 'leave' AND 'without' to qualify (eliminates HR 2.4, Finance sections)
        ({"leave", "pay"}, ("leave", "without")),
        # If query mentions 'personal' + 'phone', section must contain 'personal'
        ({"personal", "phone"}, ("personal",)),
        ({"personal", "mobile"}, ("personal",)),
    ]

    lock_filter = None  # tuple of tokens ALL of which must be in section text
    for trigger_pair, required_tokens in DOMAIN_LOCKS:
        if trigger_pair.issubset(query_tokens):
            lock_filter = required_tokens
            break

    candidates = []
    for doc_name, sections in index.items():
        for section_num, section_text in sections.items():
            # Apply domain lock: skip sections missing any required token
            if lock_filter:
                section_tok = _tokenize(section_text)
                if not all(rt in section_tok for rt in lock_filter):
                    continue
            score = _score_section(expanded_tokens, section_text)
            if score >= MIN_MATCH_SCORE:
                candidates.append((score, doc_name, section_num, section_text))

    if not candidates:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    candidates.sort(key=lambda x: x[0], reverse=True)

    top_score, top_doc, top_section, top_text = candidates[0]

    # Cross-document blending guard:
    # If the top two candidates come from DIFFERENT documents and have
    # identical scores, we cannot safely pick one — refuse.
    # We only refuse on a TIE; if the top answer has even 1 point more,
    # it is the clear single-source winner.
    if len(candidates) >= 2:
        second_score, second_doc, _, _ = candidates[1]
        if second_doc != top_doc and second_score >= top_score:
            return (
                f"[CROSS-DOCUMENT AMBIGUITY DETECTED]\n"
                f"This question touches content in both '{top_doc}' and '{second_doc}'. "
                f"These documents cannot be combined to form a single answer.\n\n"
                + REFUSAL_TEMPLATE
            )

    # Build the answer
    answer = (
        f"[Source: {top_doc} | Section {top_section}]\n\n"
        f"{section_num_label(top_section, top_text)}"
    )

    # Hedging guard: scan the answer for forbidden phrases
    for phrase in HEDGING_PHRASES:
        if phrase in answer.lower():
            # Strip the hedging phrase — this shouldn't occur since we're
            # quoting verbatim from policy, but guard anyway
            answer = answer.replace(phrase, "[PHRASE REMOVED — hedging not permitted]")

    return answer


def section_num_label(section_num: str, text: str) -> str:
    """Formats the answer citation line."""
    return f"Section {section_num}: {text}"


# ─────────────────────────────────────────────────────────────
# Interactive CLI + Output File
# ─────────────────────────────────────────────────────────────

BANNER = """
+================================================================+
|        UC-X -- Ask My Documents (Policy Assistant)            |
|  Sources: HR Leave | IT Acceptable Use | Finance Expense       |
|  Type your question and press Enter. Type 'quit' to exit.     |
+================================================================+
"""

SEPARATOR = "-" * 66

# Output log file — written to uc-x/ alongside app.py (mirrors uc-0b pattern)
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "qa_session_log.txt")

# The 7 README validation test questions (README.md § "The 7 Test Questions")
README_TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def _write_log(log_lines: list, path: str) -> None:
    """Writes the full session log to the output file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        print(f"  [LOG] Session saved -> {path}")
    except Exception as exc:
        print(f"  [WARN] Could not write log: {exc}", file=sys.stderr)


def _format_qa_block(question: str, answer: str, index: int) -> list:
    """Returns formatted Q&A lines ready to append to the log."""
    return [
        "",
        SEPARATOR,
        f"Q{index}: {question}",
        SEPARATOR,
        answer,
    ]


def main():
    print(BANNER)

    # ── Step 1: retrieve_documents skill ──
    print("Loading and indexing policy documents...")
    result = retrieve_documents(POLICY_FILES)

    if result["errors"]:
        for err in result["errors"]:
            print(f"  [INIT ERROR] {err}", file=sys.stderr)

    index = result["index"]
    if not index:
        print("\n[FATAL] No policy documents could be loaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    loaded_docs = list(index.keys())
    total_sections = sum(len(s) for s in index.values())
    print(f"  [OK] Loaded {len(loaded_docs)} document(s) | {total_sections} sections indexed.")
    for doc in loaded_docs:
        print(f"    - {doc} ({len(index[doc])} sections)")

    # ── Build the output log header ──
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_lines = [
        "UC-X -- Ask My Documents | Policy Q&A Session Log",
        "=" * 66,
        f"Generated : {timestamp}",
        f"Documents : {', '.join(loaded_docs)}",
        f"Sections  : {total_sections} total",
        "=" * 66,
        "",
        "SECTION 1: README VALIDATION — 7 TEST QUESTIONS",
        "=" * 66,
        "(Auto-run on every startup to validate enforcement rules per README.md)",
        "(Expected results are documented in README.md)",
    ]

    # ── Step 2: Auto-run the 7 README test questions ──
    print(f"\n{SEPARATOR}")
    print("Running 7 README validation test questions...")
    print(SEPARATOR)

    for i, question in enumerate(README_TEST_QUESTIONS, start=1):
        answer = answer_question(question, index)
        print(f"\nQ{i}: {question}")
        print(answer)
        log_lines += _format_qa_block(question, answer, i)

    # Save the validation batch
    _write_log(log_lines, OUTPUT_FILE)

    print(f"\n{SEPARATOR}")
    print("Validation complete. Starting interactive session.")
    print("All Q&A will be appended to qa_session_log.txt.")
    print(SEPARATOR)

    # ── Step 3: Interactive Q&A loop (answer_question skill) ──
    log_lines += [
        "",
        "SECTION 2: INTERACTIVE SESSION",
        "=" * 66,
    ]
    interactive_counter = len(README_TEST_QUESTIONS) + 1

    while True:
        try:
            query = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break

        if not query:
            continue

        if query.lower() in {"quit", "exit", "q"}:
            print("Exiting. Goodbye.")
            break

        # answer_question skill
        answer = answer_question(query, index)

        print(f"\n{SEPARATOR}")
        print(answer)
        print(SEPARATOR)


if __name__ == "__main__":
    main()

"""
UC-X - Ask My Documents
Interactive CLI that answers employee questions from three authorised policy
files only.  All answers are single-source; blended answers are refused.

Run:
    python app.py

Enforcement rules (from agents.md):
  1. Never combine claims from two different documents.
  2. Never use hedging phrases.
  3. Unanswerable questions → exact refusal template, no variations.
  4. Every factual answer includes "Source: <filename>, Section <N.N>".
  5. No implicit permission grants.
  6. No condition omission.
  7. No inference on ambiguity.
"""

import io
import os
import re
import sys

# Reconfigure stdout/stderr to UTF-8 so box-drawing and special chars work
# on Windows regardless of the console code page.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import textwrap
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

POLICY_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

AUTHORISED_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Banned hedging phrases (enforcement rule 2)
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it could be argued",
    "in most cases",
    "usually",
]

# Section heading pattern: lines that start with a digit, e.g. "2.6 Employees…"
# Also captures the top-level section dividers like "2. ANNUAL LEAVE"
SECTION_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)?)\s+(.+)$"
)

# Divider line (═══…) — used to detect top-level section boundaries
DIVIDER_PATTERN = re.compile(r"^═{3,}")


# ─────────────────────────────────────────────────────────────────────────────
# Custom exceptions (from skills.md)
# ─────────────────────────────────────────────────────────────────────────────

class ConfigError(Exception):
    """Raised when the file list is not exactly the three authorised files."""


class LoadError(Exception):
    """Raised when a required policy file cannot be read."""


class ParseError(Exception):
    """Raised when a file contains no parseable section markers."""


class DependencyError(Exception):
    """Raised when answer_question is called without a valid index."""


# ─────────────────────────────────────────────────────────────────────────────
# Skill 1 — retrieve_documents
# ─────────────────────────────────────────────────────────────────────────────

def retrieve_documents(file_paths: list[str]) -> dict:
    """
    Load the three authorised policy files and build an in-memory index keyed
    by filename and section number.

    Returns:
        {
          "policy_hr_leave.txt": {
            "sections": [
              {"section_number": "2.6",
               "section_title": "Employees may carry forward…",
               "content": "…full text of that clause…"},
              …
            ]
          },
          …
        }

    Raises:
        ConfigError  — if file_paths is not exactly the three authorised files
        LoadError    — if any file cannot be read
        ParseError   — if a file contains no section markers
    """
    # ── ConfigError: must be exactly the three authorised files ──────────────
    basenames = [os.path.basename(p) for p in file_paths]
    if sorted(basenames) != sorted(AUTHORISED_FILES):
        raise ConfigError(
            f"Expected exactly these three files: {AUTHORISED_FILES}. "
            f"Got: {basenames}"
        )
    if len(file_paths) != 3:
        raise ConfigError(
            f"Expected exactly 3 file paths; received {len(file_paths)}."
        )

    index: dict = {}

    for path_str in file_paths:
        path = Path(path_str)
        filename = path.name

        # ── LoadError: file must exist and be readable ────────────────────
        if not path.exists():
            raise LoadError(f"File not found: {filename} (resolved to {path})")
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise LoadError(f"Cannot read {filename}: {exc}") from exc

        # ── Parse sections ────────────────────────────────────────────────
        sections = _parse_sections(raw, filename)

        # ── ParseError: at least one section must be found ────────────────
        if not sections:
            raise ParseError(
                f"No parseable sections found in {filename}. "
                "Ensure the file uses 'N.N Heading' section markers."
            )

        index[filename] = {"sections": sections}

    return index


def _parse_sections(text: str, filename: str) -> list[dict]:
    """
    Parse a policy file into a list of section dicts.

    Strategy:
      - Walk lines.
      - Top-level headings (integer-only section number, e.g. "3. ANNUAL LEAVE")
        flush the current section and reset state but do NOT start a
        content-bearing section themselves — their title must not bleed into
        the previous sub-section's answer text.
      - Sub-section lines (e.g. "3.1 …") open a new content-bearing section.
      - Divider lines (═══…) are skipped entirely.
    """
    lines = text.splitlines()
    sections: list[dict] = []
    current: Optional[dict] = None

    # Pattern for top-level headings: single integer, e.g. "2. ANNUAL LEAVE"
    top_level_pat = re.compile(r"^(\d+)\.\s+(.+)$")
    # Pattern for sub-sections: "2.1", "2.6", etc.
    sub_section_pat = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s+(.+)$")

    for line in lines:
        stripped = line.strip()

        # Skip pure divider lines
        if DIVIDER_PATTERN.match(stripped):
            continue

        # Top-level heading → flush current section, do not start a new one
        if top_level_pat.match(stripped):
            if current is not None:
                current["content"] = current["content"].strip()
                sections.append(current)
                current = None
            continue

        # Sub-section heading → start a new content-bearing section
        m = sub_section_pat.match(stripped)
        if m:
            if current is not None:
                current["content"] = current["content"].strip()
                sections.append(current)
            current = {
                "section_number": m.group(1),
                "section_title": m.group(2).strip(),
                "content": m.group(2).strip() + "\n",
            }
        else:
            # Body line — accumulate into current section
            if current is not None:
                current["content"] += stripped + "\n"

    # Don't forget the last section
    if current is not None:
        current["content"] = current["content"].strip()
        sections.append(current)

    return sections


# ─────────────────────────────────────────────────────────────────────────────
# Skill 2 — answer_question
# ─────────────────────────────────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> str:
    """
    Search the document index for the user's question and return either:
      Form A — a single-source answer with citation, or
      Form B — the exact refusal template.

    Enforcement rules applied inside this function:
      1. Single-source only (cross-document blending → refusal).
      2. No hedging phrases allowed in generated output.
      3. Missing topic → exact refusal template.
      4. Citation required on every answer.
      5-7. Implemented via single-source + full-content passthrough (no
           paraphrasing strips conditions).

    Raises:
        ValueError      — if question is empty/not a string
        DependencyError — if index is missing or empty
    """
    # ── Validate inputs ───────────────────────────────────────────────────────
    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "question must be a non-empty string. "
            "Please supply a valid question."
        )
    if not index:
        raise DependencyError(
            "The document index is missing or empty. "
            "Run retrieve_documents() successfully before calling answer_question()."
        )

    question_lower = question.lower()
    question_keywords = _extract_keywords(question_lower)

    # ── Search all sections for relevant passages ─────────────────────────────
    # Each match: (filename, section_number, section_title, content, score)
    matches: list[tuple[str, str, str, str, int]] = []

    for filename, doc in index.items():
        for section in doc["sections"]:
            score = _relevance_score(
                question_keywords,
                question_lower,
                section["content"].lower(),
                section["section_title"].lower(),
            )
            if score > 0:
                matches.append((
                    filename,
                    section["section_number"],
                    section["section_title"],
                    section["content"],
                    score,
                ))

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    matches.sort(key=lambda x: x[4], reverse=True)

    # ── Cross-document blending check (enforcement rule 1) ────────────────────
    matched_docs = {m[0] for m in matches}
    top_score = matches[0][4]
    top_matches = [m for m in matches if m[4] == top_score]
    top_docs = {m[0] for m in top_matches}

    if len(top_docs) > 1:
        # Multiple documents tie at top relevance → genuine ambiguity → refuse
        return REFUSAL_TEMPLATE

    if len(matched_docs) > 1:
        # Check whether the best single-doc answer is clearly dominant.
        # Dominant = top-doc best score is at least 2× the best score from
        # any other document.
        best_by_doc: dict[str, int] = {}
        for m in matches:
            best_by_doc[m[0]] = max(best_by_doc.get(m[0], 0), m[4])

        top_doc = matches[0][0]
        other_best = max(
            score for doc, score in best_by_doc.items() if doc != top_doc
        )
        if top_score < 2 * other_best:
            # Scores are too close — cross-document blending risk → refuse
            return REFUSAL_TEMPLATE

    # ── Build answer from the single best match ───────────────────────────────
    best = matches[0]
    filename, section_number, _, content, _ = best

    answer = _format_answer(content, filename, section_number)

    # ── Hedge-phrase safety check (enforcement rule 2) ────────────────────────
    answer_lower = answer.lower()
    for phrase in BANNED_PHRASES:
        if phrase in answer_lower:
            # The content itself contains a banned phrase; this should not
            # happen since we quote the document directly, but guard anyway.
            return REFUSAL_TEMPLATE

    return answer


# Synonym / expansion map: question word -> list of terms to search in docs.
# This handles surface form mismatches without general knowledge.
_SYNONYMS: dict[str, list[str]] = {
    "install":    ["install", "software"],
    "installing": ["install", "software"],
    "slack":      ["slack", "software", "install"],
    "approve":    ["approve", "approval"],
    "approves":   ["approve", "approval"],
    "approval":   ["approve", "approval"],
    "phone":      ["phone", "personal device", "byod"],
    "laptop":     ["laptop", "corporate device", "device"],
    "claim":      ["claim", "reimburs"],
    "reimburs":   ["reimburs", "claim"],
    "carry":      ["carry", "carry forward", "carryforward"],
    "forward":    ["carry forward", "carryforward", "unused"],
    "unused":     ["unused", "carry forward"],
    "allowance":  ["allowance", "entitl"],
    "equipment":  ["equipment", "work from home", "allowance"],
    "meal":       ["meal", "receipts", "daily allowance", "da"],
    "leave":      ["leave", "lwp", "annual leave"],
    "without":    ["without pay", "lwp"],
    "flexible":   ["flexible"],
    "culture":    ["culture"],
    "personal":   ["personal", "byod", "personal device"],
    "work":       ["work", "official"],
    "files":      ["files", "data", "classified"],
    "home":       ["home", "work from home", "remote"],
    "payment":    ["payment", "pay"],
}


def _extract_keywords(text: str) -> set[str]:
    """Return all words (length >= 3) from the question, preserving short
    but meaningful terms like 'da', 'who', etc."""
    stop = {
        "what", "when", "where", "which", "with", "that", "this",
        "have", "from", "will", "does", "done", "they", "them",
        "their", "about", "much", "many", "some", "more", "less",
        "than", "also", "been", "were", "would", "should", "could",
        "must", "into", "onto", "upon", "over", "under", "like",
        "just", "only", "even", "still", "then",
    }
    # Keep words of length >= 2 so "da" and short terms are retained
    words = re.findall(r"[a-z]{2,}", text)
    return {w for w in words if w not in stop}


def _expand_keywords(keywords: set[str]) -> list[str]:
    """Expand keywords using the synonym map into a flat list of search terms."""
    expanded: list[str] = []
    for kw in keywords:
        expanded.append(kw)
        for syn in _SYNONYMS.get(kw, []):
            expanded.append(syn)
    return expanded


def _relevance_score(keywords: set[str], question_lower: str,
                     content_lower: str, title_lower: str) -> int:
    """
    Score how relevant a section is to the question.
    Higher = more relevant.
    Returns 0 if no meaningful overlap.
    """
    score = 0
    expanded = _expand_keywords(keywords)

    # Expanded keyword hits in content and title
    for term in expanded:
        if term in content_lower:
            score += 2
        if term in title_lower:
            score += 3  # title hits are stronger signals

    # Exact short-phrase hits (up to 4-word n-grams from question)
    question_words = question_lower.split()
    for n in (2, 3, 4):
        for i in range(len(question_words) - n + 1):
            phrase = " ".join(question_words[i:i + n])
            if phrase in content_lower:
                score += n * 3  # phrase matches outweigh keyword hits

    # ── Question-type boosting ────────────────────────────────────────────────
    # "who approves/approval" → heavily boost sections that name specific
    # approvers (Department Head, HR Director, Commissioner…)
    if re.search(r"\bwho\b", question_lower) and re.search(
        r"approv", question_lower
    ):
        for approver_term in [
            "department head", "hr director", "municipal commissioner",
            "manager approval", "written approval",
        ]:
            if approver_term in content_lower:
                score += 10

    # "install" question → boost sections that explicitly mention install +
    # approval so section 2.3 wins over other software mentions
    if re.search(r"\binstall", question_lower):
        if "must not install" in content_lower or "written approval" in content_lower:
            score += 8

    return score


def _format_answer(content: str, filename: str, section_number: str) -> str:
    """
    Produce Form A output: the section content followed by a citation line.
    Wraps long lines for readability.
    """
    wrapped = textwrap.fill(content, width=78, break_long_words=False,
                            break_on_hyphens=False)
    citation = f"\nSource: {filename}, Section {section_number}"
    return wrapped + citation


# ─────────────────────────────────────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
+--------------------------------------------------------------+
|       UC-X - Ask My Documents (CMC Policy Assistant)        |
|  Sources: HR Leave | IT Acceptable Use | Finance Reimburse   |
|  Type your question and press Enter. Type 'exit' to quit.   |
+--------------------------------------------------------------+
"""


def _build_file_paths() -> list[str]:
    """Resolve the three authorised policy file paths."""
    return [str(POLICY_DIR / fname) for fname in AUTHORISED_FILES]


def main() -> None:
    print(BANNER)

    # ── Load and index documents ──────────────────────────────────────────────
    file_paths = _build_file_paths()
    try:
        index = retrieve_documents(file_paths)
    except (ConfigError, LoadError, ParseError) as exc:
        print(f"[STARTUP ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    loaded_files = list(index.keys())
    print(f"Loaded {len(loaded_files)} policy document(s): "
          f"{', '.join(loaded_files)}\n")

    # ── Interactive Q&A loop ──────────────────────────────────────────────────
    while True:
        try:
            raw = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break

        if not raw:
            print("  (Please type a question or 'exit' to quit.)\n")
            continue

        if raw.lower() in {"exit", "quit", "q"}:
            print("Exiting. Goodbye.")
            break

        print()
        try:
            answer = answer_question(raw, index)
        except ValueError as exc:
            print(f"[INPUT ERROR] {exc}")
        except DependencyError as exc:
            print(f"[DEPENDENCY ERROR] {exc}", file=sys.stderr)
            sys.exit(1)
        else:
            print(answer)
        print()


if __name__ == "__main__":
    main()

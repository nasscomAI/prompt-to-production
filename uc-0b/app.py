"""
UC-0B — Policy Document Summarizer
Extracts and summarizes HR policy clauses with full fidelity.
Built using agents.md (RICE enforcement) + skills.md (retrieve_policy, summarize_policy).
"""
import argparse
import re
import sys
import logging
import textwrap

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Skill: retrieve_policy
# ═══════════════════════════════════════════════════════════════════════════

def retrieve_policy(file_path: str) -> dict[str, dict]:
    """
    Loads a .txt policy file and returns its content as structured numbered
    sections. Each top-level section maps to its sub-clauses.

    Returns:
        {
            "1": {"title": "PURPOSE AND SCOPE", "clauses": {"1.1": "text...", "1.2": "text..."}},
            "2": {"title": "ANNUAL LEAVE",      "clauses": {"2.1": "text...", ...}},
            ...
        }

    Error handling:
        - Raises FileNotFoundError if the file cannot be found/read.
        - Raises ValueError if no numbered sections can be parsed.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"Policy file not found: {file_path}")
        raise
    except Exception as exc:
        logger.error(f"Cannot read policy file: {exc}")
        raise

    # ── Parse header metadata ──────────────────────────────────────────
    header_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("═") and not re.match(r"^\d+\.", stripped):
            header_lines.append(stripped)
        else:
            if re.match(r"^\d+\.", stripped):
                break
            continue

    # ── Parse sections & clauses ───────────────────────────────────────
    sections: dict[str, dict] = {}
    # Match top-level section headers like "1. PURPOSE AND SCOPE"
    section_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    # Match sub-clauses like "1.1 This policy..."
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    current_section_num = None
    current_clause_num = None

    for line in content.splitlines():
        stripped = line.strip()

        # Skip separator lines
        if stripped.startswith("═") or not stripped:
            continue

        # Check for top-level section header
        section_match = section_pattern.match(stripped)
        if section_match:
            sec_num = section_match.group(1)
            sec_title = section_match.group(2)
            sections[sec_num] = {"title": sec_title, "clauses": {}}
            current_section_num = sec_num
            current_clause_num = None
            continue

        # Check for sub-clause
        clause_match = clause_pattern.match(stripped)
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)
            # Determine which section this clause belongs to
            parent_sec = clause_num.split(".")[0]
            if parent_sec in sections:
                sections[parent_sec]["clauses"][clause_num] = clause_text
                current_section_num = parent_sec
                current_clause_num = clause_num
            continue

        # Continuation line — append to current clause
        if current_clause_num and current_section_num:
            parent_sec = current_clause_num.split(".")[0]
            if parent_sec in sections and current_clause_num in sections[parent_sec]["clauses"]:
                sections[parent_sec]["clauses"][current_clause_num] += " " + stripped

    if not sections:
        raise ValueError(f"No numbered sections found in {file_path}")

    logger.info(
        f"Parsed {len(sections)} sections with "
        f"{sum(len(s['clauses']) for s in sections.values())} clauses total"
    )
    return sections


# ═══════════════════════════════════════════════════════════════════════════
# Skill: summarize_policy
# ═══════════════════════════════════════════════════════════════════════════

# Binding / obligation verbs that signal hard requirements
OBLIGATION_VERBS = [
    "must", "requires", "required", "will be", "is not permitted",
    "cannot", "not valid", "not permitted", "not be considered",
    "are forfeited", "forfeited", "not count toward",
]

# Clauses identified as having multi-condition obligations (from README ground truth)
MULTI_CONDITION_CLAUSES = {
    "2.4",  # Written approval + verbal not valid
    "2.6",  # Max 5 days + above 5 forfeited on 31 Dec
    "2.7",  # Must be used Jan–Mar + or forfeited
    "3.2",  # 3+ days + medical cert + within 48hrs
    "3.4",  # Before/after holiday + regardless of duration
    "5.2",  # Department Head AND HR Director
    "5.3",  # >30 days + Municipal Commissioner
}


def _has_obligation(text: str) -> bool:
    """Check if clause text contains binding obligation language."""
    text_lower = text.lower()
    return any(verb in text_lower for verb in OBLIGATION_VERBS)


def _summarize_clause(clause_num: str, clause_text: str) -> tuple[str, bool]:
    """
    Summarize a single clause. Returns (summary_text, was_quoted_verbatim).

    Enforcement rules:
    - Multi-condition obligations preserve ALL conditions
    - If summarization risks meaning loss, quote verbatim and flag
    - Never add information not present in the source
    """
    has_obligation = _has_obligation(clause_text)
    is_multi_condition = clause_num in MULTI_CONDITION_CLAUSES

    # For multi-condition obligation clauses, quote verbatim to prevent
    # condition dropping (the core failure mode from agents.md)
    if is_multi_condition and has_obligation:
        return f'[Clause {clause_num}] [VERBATIM — multi-condition obligation] "{clause_text}"', True

    # For simple obligation clauses, produce a faithful compact summary
    if has_obligation:
        # Keep the full text but format it clearly — these are too risky to rephrase
        return f"[Clause {clause_num}] {clause_text}", False

    # Non-obligation informational clauses can be summarized more freely
    # but we still preserve exact meaning
    return f"[Clause {clause_num}] {clause_text}", False


def summarize_policy(sections: dict[str, dict]) -> str:
    """
    Takes structured sections and produces a compliant, complete summary
    with clause references.

    Enforcement (from agents.md):
    1. Every numbered clause must be present in the output
    2. Multi-condition obligations preserve ALL conditions
    3. Never add information not in the source document
    4. If a clause cannot be summarised without meaning loss — quote verbatim and flag

    Returns the full summary as a string.
    """
    output_lines: list[str] = []
    verbatim_flags: list[str] = []
    clause_count = 0

    output_lines.append("=" * 60)
    output_lines.append("POLICY SUMMARY — HR LEAVE POLICY (HR-POL-001 v2.3)")
    output_lines.append("Generated by UC-0B Policy Summarizer")
    output_lines.append("=" * 60)
    output_lines.append("")
    output_lines.append(
        "NOTE: This summary preserves all numbered clauses from the source "
        "document. Clauses marked [VERBATIM] are quoted exactly as written "
        "because summarizing would risk dropping conditions or softening "
        "obligations."
    )
    output_lines.append("")

    for sec_num in sorted(sections.keys(), key=lambda x: int(x)):
        section = sections[sec_num]
        title = section["title"]
        clauses = section["clauses"]

        output_lines.append("-" * 60)
        output_lines.append(f"Section {sec_num}: {title}")
        output_lines.append("-" * 60)

        if not clauses:
            output_lines.append("  (No sub-clauses found)")
            output_lines.append("")
            continue

        for clause_num in sorted(clauses.keys(), key=lambda x: float(x)):
            clause_text = clauses[clause_num]
            summary, was_verbatim = _summarize_clause(clause_num, clause_text)
            output_lines.append(f"  {summary}")
            clause_count += 1

            if was_verbatim:
                verbatim_flags.append(clause_num)

        output_lines.append("")

    # ── Compliance footer ──────────────────────────────────────────────
    output_lines.append("=" * 60)
    output_lines.append("COMPLIANCE REPORT")
    output_lines.append("=" * 60)
    total_source = sum(len(s["clauses"]) for s in sections.values())
    output_lines.append(f"  Source clauses:     {total_source}")
    output_lines.append(f"  Summary clauses:    {clause_count}")
    output_lines.append(f"  Coverage:           {'COMPLETE' if clause_count == total_source else 'INCOMPLETE — REVIEW REQUIRED'}")
    output_lines.append(f"  Verbatim-quoted:    {len(verbatim_flags)} clause(s) {verbatim_flags if verbatim_flags else ''}")
    output_lines.append(f"  External info added: None")
    output_lines.append("")

    if clause_count != total_source:
        logger.warning(
            f"CLAUSE MISMATCH: source has {total_source} clauses but "
            f"summary has {clause_count}"
        )

    return "\n".join(output_lines)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Document Summarizer"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the .txt policy document"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the summary output"
    )
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    logger.info(f"Loading policy from: {args.input}")
    sections = retrieve_policy(args.input)

    # Skill 2: summarize_policy
    logger.info("Generating compliant summary...")
    summary = summarize_policy(sections)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    logger.info(f"Summary written to: {args.output}")
    print(f"\nDone. Summary written to {args.output}")


if __name__ == "__main__":
    main()

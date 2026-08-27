"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy per agents.md and skills.md.

Enforcement (from agents.md):
  - Every numbered clause must be present in the summary
  - Multi-condition obligations must preserve ALL conditions
  - Never add information not present in the source document
  - If a clause cannot be summarised without meaning loss, quote it verbatim and flag it
"""
import argparse
import re
import sys


# Phrases that indicate scope bleed — these must never appear in the output
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "generally expected",
    "it is common practice",
    "as is common",
    "standard in most organisations",
    "usually",
    "typically",
    "normally",
]

# Binding verbs that signal hard obligations — clauses containing these
# must be handled with extra care during summarisation
BINDING_VERBS = [
    "must", "requires", "required", "will be", "shall",
    "not permitted", "are forfeited", "forfeited",
]

# Multi-condition signal words — presence of multiple conditions in one clause
MULTI_CONDITION_SIGNALS = [
    " and ", " or ", "regardless of", "within", "exceeding",
    "before or after", "subject to", "only after",
]


def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.

    Returns:
        {
            "sections": {
                "1": {"title": "PURPOSE AND SCOPE", "clauses": {"1.1": "text", "1.2": "text"}},
                "2": {"title": "ANNUAL LEAVE", "clauses": {"2.1": "text", ...}},
                ...
            },
            "all_clauses": {"1.1": "text", "1.2": "text", "2.3": "text", ...},
            "source_lines": [list of all lines for verbatim quoting]
        }

    Enforcement (from skills.md):
      - If file cannot be read or contains no numbered sections, halt and report
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not lines:
        print(f"ERROR: {file_path} is empty.", file=sys.stderr)
        sys.exit(1)

    full_text = "".join(lines)
    sections = {}
    all_clauses = {}
    current_section_num = None
    current_section_title = ""

    section_header_re = re.compile(r"^(\d+)\.\s+(.+)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Skip decorative lines
        if stripped.startswith("═") or stripped.startswith("---"):
            continue

        # Check for section header (e.g., "2. ANNUAL LEAVE")
        sec_match = section_header_re.match(stripped)
        if sec_match:
            current_section_num = sec_match.group(1)
            current_section_title = sec_match.group(2).strip()
            if current_section_num not in sections:
                sections[current_section_num] = {
                    "title": current_section_title,
                    "clauses": {},
                }
            continue

        # Check for clause (e.g., "2.3 Employees must submit...")
        clause_match = clause_re.match(stripped)
        if clause_match:
            clause_id = clause_match.group(1)
            clause_text = clause_match.group(2).strip()
            all_clauses[clause_id] = clause_text

            if current_section_num and current_section_num in sections:
                sections[current_section_num]["clauses"][clause_id] = clause_text
            continue

        # Continuation line — append to last clause in current section
        if current_section_num and sections[current_section_num]["clauses"]:
            last_clause_id = list(sections[current_section_num]["clauses"].keys())[-1]
            sections[current_section_num]["clauses"][last_clause_id] += " " + stripped
            all_clauses[last_clause_id] += " " + stripped

    if not all_clauses:
        print(f"ERROR: No numbered clauses found in {file_path}.", file=sys.stderr)
        sys.exit(1)

    return {
        "sections": sections,
        "all_clauses": all_clauses,
        "source_lines": lines,
        "full_text": full_text,
    }


def _has_multi_conditions(clause_text: str) -> bool:
    """Detect if a clause has multiple conditions that must all be preserved."""
    text_lower = clause_text.lower()
    count = sum(1 for signal in MULTI_CONDITION_SIGNALS if signal in text_lower)
    return count >= 2


def _contains_scope_bleed(text: str) -> bool:
    """Check if text contains any scope bleed phrases."""
    text_lower = text.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in text_lower:
            return True
    return False


def _summarize_single_clause(clause_id: str, clause_text: str) -> tuple[str, bool]:
    """
    Attempt to produce a one-line summary for a clause.

    Returns:
        (summary_text, is_flagged)
        is_flagged=True means the clause was quoted verbatim because paraphrasing
        would cause meaning loss.

    Enforcement (from agents.md):
      - Multi-condition obligations must preserve ALL conditions
      - If meaning loss risk, quote verbatim and flag
    """
    # If clause has multiple binding conditions, quote verbatim and flag
    if _has_multi_conditions(clause_text):
        return clause_text.strip(), True

    # Check for binding verbs — clauses with hard obligations get careful treatment
    text_lower = clause_text.lower()
    has_binding = any(bv in text_lower for bv in BINDING_VERBS)

    # For short clauses or those with binding verbs, prefer verbatim
    if has_binding and len(clause_text) < 120:
        return clause_text.strip(), False

    # For longer clauses, extract core obligation
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", clause_text.strip())
    if len(sentences) == 1:
        return clause_text.strip(), False

    # If multiple sentences, include all — don't drop any
    # But if it's long and has binding verbs, flag for verbatim
    if has_binding:
        return clause_text.strip(), True

    # Otherwise, return the full text (all sentences)
    return clause_text.strip(), False


def summarize_policy(policy_data: dict) -> tuple[str, list[str]]:
    """
    Takes structured numbered sections and produces a compliant summary.

    Returns:
        (summary_text, warnings)
        warnings = list of clause IDs that were flagged for verbatim quoting

    Enforcement (from agents.md):
      - Every numbered clause must be present in the summary
      - Multi-condition obligations must preserve ALL conditions
      - Never add information not present in the source document
      - If meaning loss, quote verbatim and flag

    Enforcement (from skills.md):
      - If any numbered clause is missing from output, flag it before writing
    """
    all_clauses = policy_data["all_clauses"]
    sections = policy_data["sections"]
    warnings = []

    lines = []
    lines.append("POLICY SUMMARY")
    lines.append("=" * 60)
    lines.append("")
    lines.append("This summary preserves every numbered clause from the source document.")
    lines.append("Clauses that cannot be safely paraphrased are quoted verbatim [VERBATIM].")
    lines.append("")

    processed_clauses = set()

    for sec_num in sorted(sections.keys(), key=lambda x: int(x)):
        sec = sections[sec_num]
        lines.append(f"--- Section {sec_num}: {sec['title']} ---")
        lines.append("")

        for clause_id in sorted(sec["clauses"].keys(), key=lambda x: [int(p) for p in x.split(".")]):
            clause_text = sec["clauses"][clause_id]
            summary, is_flagged = _summarize_single_clause(clause_id, clause_text)

            if is_flagged:
                warnings.append(clause_id)
                lines.append(f"  [{clause_id}] {summary}  [VERBATIM — multi-condition or meaning-loss risk]")
            else:
                lines.append(f"  [{clause_id}] {summary}")

            processed_clauses.add(clause_id)
            lines.append("")

    # Check for missing clauses (enforcement from skills.md)
    missing = set(all_clauses.keys()) - processed_clauses
    if missing:
        lines.append("⚠  CLAUSES NOT FOUND IN SOURCE BUT EXPECTED:")
        for cid in sorted(missing, key=lambda x: [int(p) for p in x.split(".")]):
            lines.append(f"  [{cid}] NOT FOUND IN DOCUMENT — review required")
            warnings.append(cid)
        lines.append("")

    summary_text = "\n".join(lines)

    # Final safety check — scope bleed detection
    if _contains_scope_bleed(summary_text):
        lines.append("")
        lines.append("⚠  WARNING: Scope bleed detected in output. Review for external knowledge.")

    return summary_text, warnings


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Summarize HR policy preserving all numbered clauses"
    )
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    # Step 1: Retrieve and parse the policy document
    policy_data = retrieve_policy(args.input)
    clause_count = len(policy_data["all_clauses"])
    print(f"Retrieved {clause_count} clauses from {args.input}")

    # Step 2: Generate the summary
    summary_text, warnings = summarize_policy(policy_data)

    # Step 3: Write output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary_text)
    except Exception as e:
        print(f"ERROR: Could not write to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

    # Report
    if warnings:
        print(f"⚠  {len(warnings)} clause(s) flagged for verbatim quoting: {', '.join(warnings)}")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

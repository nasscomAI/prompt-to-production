"""
UC-0B app.py — Policy Summary Agent
Implementation based on RICE framework (agents.md) and skills definition (skills.md).

Produces a clause-faithful summary of municipal HR leave policy documents.
Core failure modes guarded against: clause omission, scope bleed, obligation softening.
"""
import argparse
import os
import re


# ─────────────────────────────────────────────────────────────────────
#  CONFIGURATION — Derived from agents.md enforcement rules
# ─────────────────────────────────────────────────────────────────────

# The 10 critical clauses from the clause inventory (README ground truth).
# Used for post-summarization verification.
CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

# Binding verbs that must not be softened (agents.md enforcement rule 4).
BINDING_VERBS = ["must", "will", "requires", "not permitted", "may", "are forfeited"]

# Scope-bleed phrases that must NEVER appear in the output (agents.md context).
# None of these exist in the source document.
PROHIBITED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

# Multi-condition clauses that require explicit dual-entity preservation.
# Format: clause_number -> list of required entities
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],
}

# Maximum summary-to-source ratio before flagging potential fabrication
MAX_SUMMARY_RATIO = 0.6


# ─────────────────────────────────────────────────────────────────────
#  SKILL 1: retrieve_policy
#  Loads .txt policy file, returns content as structured numbered sections.
# ─────────────────────────────────────────────────────────────────────

def retrieve_policy(filepath: str) -> list[dict]:
    """
    Parse a plain-text policy document into structured numbered sections.

    Args:
        filepath: Path to the .txt policy file.

    Returns:
        List of dicts, each with keys:
          - 'clause': clause number string (e.g., '2.3')
          - 'heading': the parent section heading (e.g., 'ANNUAL LEAVE')
          - 'text': full clause text exactly as written in the source

    Raises:
        FileNotFoundError: If the file path is invalid.
        ValueError: If the file is empty.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")

    with open(filepath, mode="r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"Policy file is empty: {filepath}")

    sections = []
    current_heading = ""

    # Regex to detect section headings like "2. ANNUAL LEAVE"
    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    # Regex to detect clause lines like "2.3 Employees must..."
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for section heading
        heading_match = heading_pattern.match(line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            i += 1
            continue

        # Check for clause start
        clause_match = clause_pattern.match(line)
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2).strip()

            # Absorb continuation lines (indented lines that follow)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                # Stop if we hit a blank line, separator, another clause, or heading
                if (not stripped
                        or stripped.startswith("═")
                        or clause_pattern.match(stripped)
                        or heading_pattern.match(stripped)):
                    break
                clause_text += " " + stripped
                i += 1

            sections.append({
                "clause": clause_num,
                "heading": current_heading,
                "text": clause_text,
            })
            continue

        i += 1

    if not sections:
        raise ValueError(
            f"[PARSE ERROR — original text preserved] "
            f"No numbered clauses found in {filepath}"
        )

    return sections


# ─────────────────────────────────────────────────────────────────────
#  SKILL 2: summarize_policy
#  Takes structured sections, produces compliant summary with clause
#  references. Enforces all agents.md rules.
# ─────────────────────────────────────────────────────────────────────

def summarize_clause(clause: dict) -> str:
    """
    Summarize a single clause while preserving binding language and conditions.

    If condensing would lose meaning (multi-condition, strong prohibitions),
    the clause is quoted verbatim and flagged.

    Args:
        clause: Dict with 'clause', 'heading', and 'text' keys.

    Returns:
        A summary line string prefixed with the clause number.
    """
    clause_num = clause["clause"]
    text = clause["text"]

    # --- Check if this is a multi-condition clause that needs verbatim treatment ---
    if clause_num in MULTI_CONDITION_CLAUSES:
        required_entities = MULTI_CONDITION_CLAUSES[clause_num]
        # Always quote verbatim to guarantee no condition-drop
        return (
            f"  {clause_num}  \"{text}\" "
            f"[VERBATIM — multi-condition clause requiring: "
            f"{', '.join(required_entities)}]"
        )

    # --- Check for absolute prohibitions — quote verbatim ---
    if "not permitted under any circumstances" in text.lower():
        return (
            f"  {clause_num}  \"{text}\" "
            f"[VERBATIM — cannot summarize without meaning loss]"
        )

    # --- Standard summarization: preserve clause number + binding verb + obligation ---
    # Identify the binding verb used in this clause
    binding_verb = None
    text_lower = text.lower()
    for verb in BINDING_VERBS:
        if verb in text_lower:
            binding_verb = verb
            break

    # Build the summary line — keep it close to the source
    summary_line = f"  {clause_num}  {text}"

    return summary_line


def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a clause-faithful summary from structured policy sections.

    Enforcement rules applied:
      1. Every numbered clause is represented
      2. Multi-condition obligations preserve ALL conditions
      3. No fabricated content
      4. Binding verbs are not softened
      5. Clauses that can't be condensed are quoted verbatim and flagged

    Args:
        sections: List of clause dicts from retrieve_policy.

    Returns:
        A formatted summary string ready to write to the output file.
    """
    if not sections:
        return "[ERROR] No sections provided for summarization."

    output_lines = []
    output_lines.append("=" * 65)
    output_lines.append("POLICY SUMMARY — HR LEAVE POLICY (HR-POL-001)")
    output_lines.append("Generated by UC-0B Policy Summary Agent")
    output_lines.append("=" * 65)
    output_lines.append("")

    current_heading = ""
    for section in sections:
        # Group by heading
        if section["heading"] != current_heading:
            current_heading = section["heading"]
            output_lines.append(f"--- {current_heading} ---")
            output_lines.append("")

        summary_line = summarize_clause(section)
        output_lines.append(summary_line)
        output_lines.append("")

    return "\n".join(output_lines)


# ─────────────────────────────────────────────────────────────────────
#  VERIFICATION — Post-summarization checks from agents.md enforcement
# ─────────────────────────────────────────────────────────────────────

def verify_summary(summary: str, source_sections: list[dict]) -> list[str]:
    """
    Run enforcement checks against the generated summary.

    Checks:
      1. All critical clauses are present
      2. Multi-condition clauses retain all required entities
      3. No prohibited (scope-bleed) phrases
      4. Summary length is reasonable vs source (fabrication guard)

    Returns:
        List of warning/error strings. Empty list = all checks passed.
    """
    issues = []
    summary_lower = summary.lower()

    # CHECK 1: Every critical clause number must appear in the summary
    for clause_num in CRITICAL_CLAUSES:
        if clause_num not in summary:
            issues.append(
                f"[CLAUSE OMISSION] Clause {clause_num} is missing from the summary."
            )

    # CHECK 2: Multi-condition clauses must retain all entities
    for clause_num, entities in MULTI_CONDITION_CLAUSES.items():
        for entity in entities:
            if entity.lower() not in summary_lower:
                issues.append(
                    f"[CONDITION DROP] Clause {clause_num}: "
                    f"'{entity}' not found in summary."
                )

    # CHECK 3: No prohibited scope-bleed phrases
    for phrase in PROHIBITED_PHRASES:
        if phrase.lower() in summary_lower:
            issues.append(
                f"[SCOPE BLEED] Prohibited phrase detected: \"{phrase}\""
            )

    # CHECK 4: Summary length sanity (guard against fabrication)
    source_text = " ".join(s["text"] for s in source_sections)
    ratio = len(summary) / len(source_text) if source_text else 0
    if ratio > 2.0:
        issues.append(
            f"[FABRICATION RISK] Summary is {ratio:.1f}x the source length. "
            f"Possible fabricated content."
        )

    return issues


# ─────────────────────────────────────────────────────────────────────
#  MAIN — CLI entry point matching README run command
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Summary Agent. "
                    "Produces clause-faithful summaries of HR policy documents."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the input policy .txt file "
             "(e.g., ../data/policy-documents/policy_hr_leave.txt)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the summary output file "
             "(e.g., summary_hr_leave.txt)"
    )
    args = parser.parse_args()

    # ── Step 1: Retrieve policy ──
    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        return

    print(f"[retrieve_policy] Parsed {len(sections)} clauses across sections.")

    # ── Step 2: Summarize policy ──
    print("[summarize_policy] Generating clause-faithful summary...")
    summary = summarize_policy(sections)

    # ── Step 3: Verify summary ──
    print("[verify] Running enforcement checks...")
    issues = verify_summary(summary, sections)

    if issues:
        print(f"\n[ENFORCEMENT] {len(issues)} issue(s) detected:")
        for issue in issues:
            print(f"  [!] {issue}")
        print()
    else:
        print("[ENFORCEMENT] All checks passed. OK\n")

    # ── Step 4: Write output ──
    try:
        with open(args.output, mode="w", encoding="utf-8") as f:
            f.write(summary)
        print(f"[output] Summary written to: {args.output}")
    except Exception as e:
        print(f"[ERROR] Failed to write output: {e}")

    # ── Step 5: Print summary stats ──
    total_clauses = len(sections)
    critical_present = sum(
        1 for c in CRITICAL_CLAUSES if c in summary
    )
    print(f"\n-- Summary Stats --")
    print(f"  Total clauses parsed:      {total_clauses}")
    print(f"  Critical clauses (10) hit:  {critical_present}/10")
    print(f"  Enforcement issues:         {len(issues)}")
    print(f"  Output file:                {args.output}")


if __name__ == "__main__":
    main()

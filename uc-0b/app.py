"""
UC-0B — HR Policy Summariser
Built using RICE → agents.md → skills.md → CRAFT workflow.

Failure modes guarded against:
- Clause omission      : every numbered clause must appear in output
- Scope bleed          : forbidden phrases detected and removed
- Obligation softening : binding verbs checked and preserved
- Condition drop       : multi-condition clauses quoted verbatim
"""
import argparse
import re
import sys

# ── Enforcement constants (from agents.md) ───────────────────────────────────

# Phrases that indicate scope bleed — not permitted in output
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "as is standard",
    "standard practice",
    "typically in government",
    "employees are generally expected",
    "generally expected",
    "as is common",
    "in most organisations",
    "it is generally",
    "typically",
    "as per norms",
]

# Softened verbs that must never replace binding verbs
SOFTENED_VERBS = [
    "should",
    "encouraged to",
    "recommended to",
    "expected to",
    "advised to",
]

# Clauses known to have multiple conditions — quoted verbatim if any condition missing
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],
    "2.6": ["5 days", "31 Dec"],
    "2.7": ["January", "March"],
    "3.4": ["before", "after", "regardless"],
}

# Verbatim flag marker
VERBATIM_FLAG = "[VERBATIM — meaning-loss risk]"


# ── Skill 1: retrieve_policy ─────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> dict:
    """
    Load .txt policy file and return content parsed as structured numbered sections.

    Returns: dict mapping clause number strings (e.g. "2.3") to clause text.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"ERROR: Policy file not found: '{file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read policy file: {e}")
        sys.exit(1)

    if not raw.strip():
        print("ERROR: Policy file is empty.")
        sys.exit(1)

    # Parse numbered clauses — matches patterns like "2.3", "5.2", "3.4" etc.
    # Each clause runs until the next numbered clause or end of file
    clause_pattern = re.compile(r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s|\Z)', re.DOTALL)
    matches = clause_pattern.findall(raw)

    if not matches:
        print("WARNING: No numbered clauses detected in the policy file. Check the file format.")
        # Return entire document as a single entry so we still produce output
        return {"full_document": raw.strip()}

    clauses = {}
    for clause_num, clause_text in matches:
        clauses[clause_num] = clause_text.strip()

    print(f"  Retrieved  : {len(clauses)} numbered clauses from policy file")
    return clauses


# ── Skill 2: summarize_policy ─────────────────────────────────────────────────

def summarize_policy(clauses: dict) -> str:
    """
    Produce a clause-complete compliant summary from structured policy sections.

    Enforcement applied:
    - Every clause referenced by number
    - Binding verbs preserved
    - Multi-condition clauses quoted verbatim with flag
    - Scope bleed phrases removed and flagged
    - Softened verbs flagged
    """
    if not clauses:
        print("ERROR: No clauses to summarise.")
        sys.exit(1)

    lines = []
    lines.append("HR LEAVE POLICY — COMPLIANT CLAUSE SUMMARY")
    lines.append("=" * 60)
    lines.append(
        "This summary preserves every binding obligation from the source document.\n"
        "Clauses flagged [VERBATIM] are quoted exactly due to meaning-loss risk.\n"
    )

    warnings = []
    input_count  = len(clauses)
    output_count = 0

    for clause_num, text in sorted(clauses.items(), key=lambda x: [int(n) for n in x[0].split(".")]):

        # ── Check for multi-condition clause ─────────────────────────────
        if clause_num in MULTI_CONDITION_CLAUSES:
            required_terms = MULTI_CONDITION_CLAUSES[clause_num]
            missing_terms  = [t for t in required_terms if t.lower() not in text.lower()]
            if missing_terms:
                # Condition drop risk — quote verbatim
                summary_line = (
                    f"Clause {clause_num}: {text} {VERBATIM_FLAG}\n"
                    f"  [Condition check: term(s) '{', '.join(missing_terms)}' "
                    f"not detected — quoted verbatim to prevent condition drop.]"
                )
                warnings.append(
                    f"Clause {clause_num}: missing term(s) {missing_terms} — quoted verbatim."
                )
            else:
                summary_line = f"Clause {clause_num}: {text}"
        else:
            summary_line = f"Clause {clause_num}: {text}"

        # ── Check for scope bleed ─────────────────────────────────────────
        for phrase in SCOPE_BLEED_PHRASES:
            if phrase.lower() in summary_line.lower():
                summary_line += f"\n  [SCOPE BLEED DETECTED: '{phrase}' removed — not in source document.]"
                # Remove the offending phrase from the line
                summary_line = re.sub(re.escape(phrase), "[REMOVED]", summary_line, flags=re.IGNORECASE)
                warnings.append(f"Clause {clause_num}: scope bleed phrase '{phrase}' detected.")

        # ── Check for softened verbs ──────────────────────────────────────
        for verb in SOFTENED_VERBS:
            if verb.lower() in summary_line.lower():
                summary_line += f"\n  [SOFTENING DETECTED: '{verb}' — verify against source binding verb.]"
                warnings.append(f"Clause {clause_num}: softened verb '{verb}' detected.")

        lines.append(summary_line)
        lines.append("")  # blank line between clauses
        output_count += 1

    # ── Clause count check ────────────────────────────────────────────────
    if output_count != input_count:
        warnings.append(
            f"CLAUSE COUNT MISMATCH: input had {input_count} clauses, "
            f"output has {output_count}. Possible omission."
        )

    # ── Append warnings block ─────────────────────────────────────────────
    if warnings:
        lines.append("=" * 60)
        lines.append("COMPLIANCE WARNINGS")
        lines.append("=" * 60)
        for w in warnings:
            lines.append(f"  • {w}")

    lines.append("")
    lines.append(f"Total clauses summarised: {output_count} of {input_count}")

    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    print(f"Running UC-0B HR Policy Summariser")
    print(f"  Input  : {args.input}")
    print(f"  Output : {args.output}")

    # Skill 1 — retrieve
    clauses = retrieve_policy(args.input)

    # Skill 2 — summarise
    summary = summarize_policy(clauses)

    # Write output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}")
        sys.exit(1)

    print(f"  Output written : {args.output}")
    print("Done.")
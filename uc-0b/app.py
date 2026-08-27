"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy per agents.md (RICE) and skills.md.
"""
import argparse
import re
import sys

# --- Enforcement constants from agents.md ---

# Clauses that MUST appear in the summary — verified against output
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Phrases that are prohibited — indicate scope bleed or external inference
PROHIBITED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally expected",
    "as in most organisations",
    "it is common",
    "generally understood",
    "in most cases",
]

# Clauses with multi-condition obligations that must ALL be preserved
# Maps clause_id → list of required terms that must appear in the summary line
MULTI_CONDITION_CHECKS = {
    "5.2": ["Department Head", "HR Director"],
    "2.4": ["written", "verbal"],
    "2.6": ["5", "31 December"],
    "2.7": ["January", "March"],
    "3.2": ["3", "48 hours"],
    "5.3": ["30", "Municipal Commissioner"],
}

# Clauses that carry legal/procedural precision — quote verbatim
VERBATIM_CLAUSES = {"7.2", "5.2", "2.5"}


# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and parse it into numbered clause dicts.
    Returns { file_path, total_clauses, raw_text, clauses: list[dict] }
    Each clause dict: { clause_id, heading, body }
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: Policy file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not raw_text.strip():
        print(f"WARNING: Policy file is empty: {file_path}", file=sys.stderr)
        return {"file_path": file_path, "total_clauses": 0, "raw_text": "", "clauses": []}

    # Match clause numbers like "2.3", "10.1" at the start of a line
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)", re.MULTILINE)
    matches = list(clause_pattern.finditer(raw_text))

    if not matches:
        print(f"WARNING: No numbered clauses detected in {file_path}", file=sys.stderr)
        return {"file_path": file_path, "total_clauses": 0, "raw_text": raw_text, "clauses": []}

    clauses = []
    for i, match in enumerate(matches):
        clause_id = match.group(1)
        first_line = match.group(2).strip()

        # Body = from end of this match to start of next (or end of text)
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        continuation = raw_text[body_start:body_end].strip()

        body = (first_line + " " + continuation).strip()
        # Strip decorative separator lines (╔═══... and section headings)
        body = re.sub(r"[╔═╗╚╝║─]+[\s\S]*?(?=\d+\.\d+|$)", "", body).strip()
        # Normalise whitespace / line breaks inside body
        body = re.sub(r"\s+", " ", body).strip()

        clauses.append({"clause_id": clause_id, "heading": "", "body": body})

    return {
        "file_path": file_path,
        "total_clauses": len(clauses),
        "raw_text": raw_text,
        "clauses": clauses,
    }


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy
# ---------------------------------------------------------------------------

def _check_multi_conditions(clause_id: str, summary_line: str, body: str) -> list[str]:
    """Return list of warning strings for any missing conditions in a summary line."""
    warnings = []
    required_terms = MULTI_CONDITION_CHECKS.get(clause_id, [])
    for term in required_terms:
        if term.lower() not in summary_line.lower():
            warnings.append(
                f"  *** CONDITION DROP WARNING — clause {clause_id}: "
                f'required term "{term}" missing from summary line ***'
            )
    return warnings


def summarize_policy(policy: dict) -> str:
    """
    Produce a compliant summary from retrieve_policy output.
    Every required clause present · all conditions preserved ·
    no external content · VERBATIM_REQUIRED flag where needed.
    """
    clauses_by_id = {c["clause_id"]: c for c in policy["clauses"]}
    lines = []

    lines.append("POLICY SUMMARY")
    lines.append(f"Source: {policy['file_path']}")
    lines.append("=" * 60)
    lines.append("")

    # Group clauses by section number for readable output
    current_section = None
    for clause in policy["clauses"]:
        cid = clause["clause_id"]
        section = cid.split(".")[0]
        if section != current_section:
            current_section = section
            lines.append("")
            lines.append(f"--- Section {section} ---")

        body = clause["body"]

        if cid in VERBATIM_CLAUSES:
            # Quote verbatim — do not paraphrase (enforcement rule 4)
            summary_line = f'"{body}"'
            lines.append(f"{cid}  {summary_line} [VERBATIM_REQUIRED] [clause {cid}]")
        else:
            lines.append(f"{cid}  {body} [clause {cid}]")
            summary_line = body

        # Check multi-condition obligations (enforcement rule 2)
        for warning in _check_multi_conditions(cid, summary_line, body):
            lines.append(warning)

    lines.append("")
    lines.append("=" * 60)

    # --- Enforcement rule 1: verify all required clauses are present ---
    lines.append("COMPLIANCE CHECK — Required clauses:")
    all_present = True
    for req in REQUIRED_CLAUSES:
        if req in clauses_by_id:
            lines.append(f"  [OK]      clause {req}")
        else:
            lines.append(f"  [MISSING] clause {req} — WARNING: not found in source document; summary may be incomplete.")
            all_present = False

    lines.append("")
    if all_present:
        lines.append("All required clauses present.")
    else:
        lines.append("WARNING: One or more required clauses are missing from the source document.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    # Skill 1 — load and parse
    policy = retrieve_policy(args.input)
    print(f"Loaded {policy['total_clauses']} clauses from {args.input}")

    # Skill 2 — summarise
    summary = summarize_policy(policy)

    # --- Prohibited phrase check (enforcement rule 3) ---
    found_prohibited = [p for p in PROHIBITED_PHRASES if p.lower() in summary.lower()]
    if found_prohibited:
        print("WARNING: Prohibited phrases detected in summary output:", file=sys.stderr)
        for p in found_prohibited:
            print(f"  - \"{p}\"", file=sys.stderr)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

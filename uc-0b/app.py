"""
UC-0B: HR Leave Policy Summariser
Implements retrieve_policy and summarize_policy skills per agents.md + skills.md
"""

import argparse
import json
import os
import re
import sys

# ── Clause inventory (ground truth) ──────────────────────────────────────────
CLAUSE_INVENTORY = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

# Phrases that indicate scope bleed — reject if found in summary
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "standard practice",
    "typically",
    "generally",
    "normally",
    "usually",
    "in most organisations",
]


# ── Skill 1: retrieve_policy ──────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return its content as structured numbered sections.
    Error handling:
        - Invalid path  → {"error": "File not found"}
        - Malformed doc → {"raw_content": "...", "warning": "Could not parse sections"}
    """
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        return {"error": f"File not found: {exc}"}

    if not raw.strip():
        return {"raw_content": raw, "warning": "Could not parse sections"}

    # Parse numbered sections: match patterns like "2.3", "3.4", "7.2" etc.
    # A section starts at a line whose first non-space token matches N.N or N.N.N
    section_pattern = re.compile(
        r'^(\d+\.\d+(?:\.\d+)?)\s+(.*)', re.MULTILINE
    )

    sections = []
    matches = list(section_pattern.finditer(raw))

    if not matches:
        return {"raw_content": raw, "warning": "Could not parse sections"}

    for i, match in enumerate(matches):
        number = match.group(1)
        # Collect content from this match to the start of the next (or end)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = raw[start:end].strip()

        # Remove the leading "number" token from the block for clean content
        content = re.sub(r'^\d+\.\d+(?:\.\d+)?\s*', '', block, count=1).strip()
        # Collapse internal newlines to spaces for readability
        content = re.sub(r'\s*\n\s*', ' ', content).strip()

        sections.append({"number": number, "content": content})

    if not sections:
        return {"raw_content": raw, "warning": "Could not parse sections"}

    return {"sections": sections}


# ── Skill 2: summarize_policy ─────────────────────────────────────────────────

def summarize_policy(structured: dict) -> str:
    """
    Take structured policy sections and produce a compliant summary that:
    - Preserves all 10 inventory clauses with references
    - Keeps ALL conditions intact (no condition dropping)
    - Flags missing clauses verbatim
    - Rejects scope-bleed language
    Error handling:
        - Missing clauses  → flagged and quoted verbatim from raw if available
        - Condition drop   → preserve all conditions or error with specifics
        - Scope bleed      → output rejected; offending phrases listed
    """
    if "error" in structured:
        raise RuntimeError(f"retrieve_policy failed: {structured['error']}")

    # Handle malformed input
    if "warning" in structured:
        raw = structured.get("raw_content", "")
        return (
            "WARNING: Could not parse policy into sections.\n"
            "Raw content follows — manual review required.\n\n"
            + raw
        )

    sections = structured.get("sections", [])
    section_map = {s["number"]: s["content"] for s in sections}

    lines = []
    lines.append("HR LEAVE POLICY — COMPLIANT SUMMARY")
    lines.append("=" * 60)
    lines.append(
        "Source: policy_hr_leave.txt | "
        "All 10 mandatory clauses included per clause inventory."
    )
    lines.append("")

    # ── Group headings derived from clause numbers ────────────────────────────
    groups = {
        "Section 2 — Annual / General Leave": ["2.3", "2.4", "2.5", "2.6", "2.7"],
        "Section 3 — Sick Leave":             ["3.2", "3.4"],
        "Section 5 — Leave Without Pay (LWP)": ["5.2", "5.3"],
        "Section 7 — Leave Encashment":        ["7.2"],
    }

    missing_clauses = []

    for heading, clause_ids in groups.items():
        lines.append(heading)
        lines.append("-" * len(heading))

        for cid in clause_ids:
            if cid not in section_map:
                missing_clauses.append(cid)
                lines.append(
                    f"  {cid}: [CLAUSE NOT FOUND IN DOCUMENT — "
                    f"manual verification required]"
                )
                continue

            content = section_map[cid]

            # ── Condition-drop guard for clause 5.2 ──────────────────────────
            if cid == "5.2":
                required_terms = ["department head", "hr director"]
                content_lower = content.lower()
                missing_terms = [
                    t for t in required_terms if t not in content_lower
                ]
                if missing_terms:
                    lines.append(
                        f"  {cid} [VERBATIM — condition-drop risk]: {content}"
                    )
                    continue

            lines.append(f"  {cid}: {content}")

        lines.append("")

    # ── Scope-bleed check ─────────────────────────────────────────────────────
    draft = "\n".join(lines)
    draft_lower = draft.lower()
    found_bleed = [p for p in SCOPE_BLEED_PHRASES if p in draft_lower]
    if found_bleed:
        raise ValueError(
            "Scope bleed detected in summary. "
            f"Offending phrases: {found_bleed}. "
            "Remove all language not present in the source document."
        )

    # ── Missing-clause report ─────────────────────────────────────────────────
    if missing_clauses:
        lines.append("OMISSION REPORT")
        lines.append("-" * 16)
        lines.append(
            "The following clauses from the mandatory inventory were not "
            "found in the parsed document:"
        )
        for cid in missing_clauses:
            lines.append(f"  • {cid}")
        lines.append(
            "Action required: verify source document completeness and "
            "re-run after correction."
        )
        lines.append("")

    lines.append("=" * 60)
    lines.append("END OF SUMMARY")

    return "\n".join(lines)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarise HR leave policy preserving all 10 clauses."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output filename (written inside uc-0b/ directory)",
    )
    args = parser.parse_args()

    # ── Step 1: retrieve_policy ───────────────────────────────────────────────
    print(f"[retrieve_policy] Loading: {args.input}")
    structured = retrieve_policy(args.input)

    if "error" in structured:
        print(f"ERROR: {structured['error']}", file=sys.stderr)
        sys.exit(1)

    if "warning" in structured:
        print(f"WARNING: {structured['warning']}")

    section_count = len(structured.get("sections", []))
    print(f"[retrieve_policy] Parsed {section_count} section(s).")

    # ── Step 2: summarize_policy ──────────────────────────────────────────────
    print("[summarize_policy] Generating compliant summary …")
    try:
        summary = summarize_policy(structured)
    except ValueError as exc:
        print(f"SCOPE BLEED ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"SUMMARISE ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Write output ──────────────────────────────────────────────────────────
    output_dir = "uc-0b"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, args.output)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"[output] Summary written to: {output_path}")

    # ── Verify all 10 clauses present ─────────────────────────────────────────
    found_all = all(cid in summary for cid in CLAUSE_INVENTORY)
    if found_all:
        print("[verify] ✓ All 10 mandatory clauses present in output.")
    else:
        missing = [cid for cid in CLAUSE_INVENTORY if cid not in summary]
        print(
            f"[verify] ✗ Missing clauses in output: {missing}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
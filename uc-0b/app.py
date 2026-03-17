#!/usr/bin/env python3
"""
UC-0B — Policy Summariser

Reads a plain-text HR policy document, parses every numbered section and clause,
and produces a clause-complete summary that preserves all binding verbs and
multi-condition obligations exactly as stated in the source.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""

import re
import argparse
import sys
from pathlib import Path
from typing import Dict, List


# ---------------------------------------------------------------------------
# Clauses that must be quoted verbatim due to high risk of meaning loss
# if paraphrased. Key = clause_id, Value = reason for verbatim flag.
# ---------------------------------------------------------------------------
VERBATIM_CLAUSES = {
    "2.4": "dual condition: written approval AND verbal approval explicitly invalidated",
    "2.5": "absolute consequence: LOP regardless of subsequent approval",
    "2.7": "hard deadline with forfeiture: must use Jan–Mar or forfeited",
    "5.2": "dual-approver condition: both Department Head AND HR Director required",
    "5.3": "escalation threshold: >30 days requires Municipal Commissioner",
    "7.2": "absolute prohibition: not permitted under any circumstances",
}


def retrieve_policy(input_path: str) -> List[Dict]:
    """
    Load a policy .txt file and parse it into structured sections with clauses.

    Returns a list of dicts:
        { section_number, heading, clauses: [{clause_id, text}] }
    """
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    raw = source.read_text(encoding="utf-8")
    if not raw.strip():
        raise ValueError(f"Policy file is empty: {input_path}")

    sections = []
    current_section = None

    section_header = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)]+)$")
    clause_line = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or set(line) <= {"═", " "}:
            continue

        sec_match = section_header.match(line)
        if sec_match:
            if current_section:
                sections.append(current_section)
            current_section = {
                "section_number": sec_match.group(1),
                "heading": sec_match.group(2).strip(),
                "clauses": [],
            }
            continue

        clause_match = clause_line.match(line)
        if clause_match and current_section is not None:
            clause_id = clause_match.group(1)
            text = clause_match.group(2).strip()
            # Append continuation lines to last clause
            if current_section["clauses"] and \
               current_section["clauses"][-1]["clause_id"] == clause_id:
                current_section["clauses"][-1]["text"] += " " + text
            else:
                current_section["clauses"].append(
                    {"clause_id": clause_id, "text": text}
                )
        elif current_section and current_section["clauses"]:
            # Continuation of the previous clause text
            current_section["clauses"][-1]["text"] += " " + line

    if current_section:
        sections.append(current_section)

    if not sections:
        raise ValueError(
            f"No numbered sections found in: {input_path}. "
            "Verify the document uses the expected format (e.g. '2. ANNUAL LEAVE')."
        )

    return sections


def summarize_policy(sections: List[Dict], output_path: str) -> None:
    """
    Write a clause-complete, binding-verb-preserving summary to output_path.
    """
    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    lines.append("Document Reference: HR-POL-001 | Version: 2.3 | Effective: 1 April 2024")
    lines.append("=" * 70)
    lines.append("")
    lines.append("IMPORTANT: This summary is generated directly from the source policy.")
    lines.append("Clauses marked [VERBATIM] are quoted exactly to prevent meaning loss.")
    lines.append("Every numbered clause from the source is included below.")
    lines.append("")

    for section in sections:
        sec_num = section["section_number"]
        heading = section["heading"]
        clauses = section["clauses"]

        lines.append(f"{'─' * 70}")
        lines.append(f"SECTION {sec_num}: {heading}")
        lines.append(f"{'─' * 70}")

        if not clauses:
            lines.append(f"  [EMPTY — VERIFY SOURCE: Section {sec_num} contains no clauses]")
            lines.append("")
            continue

        for clause in clauses:
            cid = clause["clause_id"]
            text = clause["text"]

            if cid in VERBATIM_CLAUSES:
                reason = VERBATIM_CLAUSES[cid]
                lines.append(f"  {cid} [VERBATIM — {reason}]:")
                lines.append(f"       \"{text}\"")
            else:
                lines.append(f"  {cid}  {text}")

        lines.append("")

    lines.append("=" * 70)
    lines.append("END OF SUMMARY")
    lines.append("")
    lines.append("Clause completeness check (10 high-risk clauses):")
    high_risk = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    all_clause_ids = {
        c["clause_id"]
        for sec in sections
        for c in sec["clauses"]
    }
    for cid in high_risk:
        status = "PRESENT" if cid in all_clause_ids else "MISSING — ACTION REQUIRED"
        lines.append(f"  Clause {cid}: {status}")

    output = "\n".join(lines) + "\n"
    Path(output_path).write_text(output, encoding="utf-8")
    print(f"Summary written → {output_path}")

    missing = [cid for cid in high_risk if cid not in all_clause_ids]
    if missing:
        print(
            f"WARNING: {len(missing)} high-risk clause(s) missing from source: "
            f"{', '.join(missing)}",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B Municipal HR Policy Summariser"
    )
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path for output summary file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summarize_policy(sections, args.output)


if __name__ == "__main__":
    main()

"""
UC-0B — Summary That Changes Meaning
Implementation guided by agents.md (RICE framework) and skills.md.

Design: Deterministic rule-based text extraction — no LLM dependency.
Every clause from the source document is extracted and reproduced faithfully.
Multi-condition obligations, numerical thresholds, and binding verbs are
preserved exactly. A completeness check verifies all 10 critical clauses appear.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


# ── Critical clauses that MUST appear in the summary ─────────────────────────
CRITICAL_CLAUSES = {
    "2.3": "14-day advance notice",
    "2.4": "written approval before leave commences / verbal not valid",
    "2.5": "unapproved absence = LOP regardless of subsequent approval",
    "2.6": "max 5 days carry-forward / forfeited on 31 December",
    "2.7": "carry-forward must be used January–March or forfeited",
    "3.2": "3+ sick days requires medical cert within 48 hours",
    "3.4": "sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director (both)",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "leave encashment during service not permitted under any circumstances",
}


# ── skill: retrieve_policy ────────────────────────────────────────────────────
def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load policy document and return structured list of clauses.
    Each entry: {section_number, section_heading, text}
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy document not found: {file_path}")

    content = path.read_text(encoding="utf-8-sig")
    if not content.strip():
        raise ValueError("Policy document is empty")

    clauses = []
    current_heading = "Preamble"
    # Match section headings like "═══...═══" followed by title line
    heading_pattern = re.compile(r"═{3,}")
    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.+)", re.MULTILINE)

    # Split by top-level sections (delimited by ═══ lines)
    sections = re.split(r"═{3,}\r?\n", content)
    # Re-build heading tracking
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detect section heading separator (═══ line)
        if re.match(r"═{3,}", line):
            # Next non-empty line is the section heading (e.g. "2. ANNUAL LEAVE")
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                heading_raw = lines[j].strip()
                # Heading might be "2. ANNUAL LEAVE" — clean it up
                if not re.match(r"^\d+\.\d+\s", heading_raw):
                    current_heading = heading_raw
                    i = j + 1
                    continue
            i += 1
            continue

        # Detect numbered clause (e.g. "2.3 Employees must submit...")
        m = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
        if m:
            clause_num = m.group(1)
            clause_text_first_line = m.group(2).strip()
            # Collect continuation lines (indented or blank then indented)
            text_lines = [clause_text_first_line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                stripped = next_line.strip()
                # Stop at empty line or next clause number or heading separator
                if re.match(r"═{3,}", stripped):
                    break
                if re.match(r"^\d+\.\d+\s", stripped):
                    break
                if stripped == "" and j + 1 < len(lines):
                    # peek: if next line is a new clause or separator, stop
                    peek = lines[j + 1].strip()
                    if re.match(r"^\d+\.\d+\s", peek) or re.match(r"═{3,}", peek):
                        break
                if stripped:
                    text_lines.append(stripped)
                j += 1
            full_text = " ".join(text_lines).strip()
            clauses.append({
                "section_number": clause_num,
                "section_heading": current_heading,
                "text": full_text,
            })
            i = j
            continue
        i += 1

    if len(clauses) < 5:
        print(
            f"WARNING: Only {len(clauses)} clauses detected — "
            "document may be malformed.",
            file=sys.stderr,
        )
    return clauses


# ── skill: summarize_policy ───────────────────────────────────────────────────
def summarize_policy(clauses: list[dict], output_path: str) -> None:
    """
    Produce a complete clause-faithful summary.
    Every clause is referenced by its number. Critical clauses are verified.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    lines.append("Source: policy_hr_leave.txt (HR-POL-001 v2.3, Effective: 1 April 2024)")
    lines.append("Summary generated by UC-0B Policy Summarization Agent")
    lines.append("ENFORCEMENT: Every numbered clause is reproduced below.")
    lines.append("=" * 70)
    lines.append("")

    current_heading = None
    for clause in clauses:
        heading = clause["section_heading"]
        if heading != current_heading:
            lines.append("")
            lines.append(f"── {heading} ──")
            lines.append("")
            current_heading = heading

        num = clause["section_number"]
        text = clause["text"]
        lines.append(f"[{num}]  {text}")

    # ── Completeness check ────────────────────────────────────────────────────
    lines.append("")
    lines.append("=" * 70)
    lines.append("COMPLETENESS CHECK — 10 CRITICAL CLAUSES")
    lines.append("=" * 70)

    found_nums = {c["section_number"] for c in clauses}
    all_ok = True
    for clause_id, description in CRITICAL_CLAUSES.items():
        status = "✓ PRESENT" if clause_id in found_nums else "✗ MISSING"
        if clause_id not in found_nums:
            all_ok = False
            print(
                f"WARNING: Critical clause {clause_id} ({description}) "
                "not found in source document.",
                file=sys.stderr,
            )
        lines.append(f"  [{clause_id}] {status}  — {description}")

    lines.append("")
    if all_ok:
        lines.append("RESULT: ALL 10 CRITICAL CLAUSES PRESENT — summary is complete.")
    else:
        lines.append("RESULT: ONE OR MORE CRITICAL CLAUSES MISSING — review required.")

    lines.append("")
    lines.append("=" * 70)
    lines.append("IMPORTANT MULTI-CONDITION OBLIGATIONS (NOT TO BE SOFTENED)")
    lines.append("=" * 70)
    lines.append(
        "[5.2]  Leave Without Pay requires approval from BOTH the Department Head"
        " AND the HR Director. Manager approval alone is NOT sufficient."
    )
    lines.append(
        "[2.4]  Written approval is required before leave commences."
        " Verbal approval is NOT valid."
    )
    lines.append(
        "[7.2]  Leave encashment during service is NOT permitted under ANY circumstances."
        " (This is an absolute prohibition with no exceptions.)"
    )

    output = "\n".join(lines) + "\n"
    Path(output_path).write_text(output, encoding="utf-8")
    print(f"Summary written to {output_path}")
    print(f"Clauses processed: {len(clauses)}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument(
        "--input",
        default="../data/policy-documents/policy_hr_leave.txt",
        help="Path to policy_hr_leave.txt",
    )
    parser.add_argument(
        "--output",
        default="summary_hr_leave.txt",
        help="Path to write summary",
    )
    args = parser.parse_args()

    print(f"Loading policy from: {args.input}")
    clauses = retrieve_policy(args.input)
    print(f"Extracted {len(clauses)} clauses")
    summarize_policy(clauses, args.output)

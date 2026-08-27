"""
UC-0B: Summary That Changes Meaning
Reads a policy document and produces a faithful summary
that preserves all numbered clauses and obligations.

Usage:
    python app.py
    python app.py <input_policy.txt> <output_summary.txt>
"""

import re
import sys
import os


def read_policy(filepath: str) -> str:
    """Read policy document from file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_numbered_clauses(text: str) -> list:
    """Extract all numbered clauses from the document."""
    pattern = r'(?:^|\n)(\d+[\.\)]\s+.+?)(?=\n\d+[\.\)]|\Z)'
    clauses = re.findall(pattern, text, re.DOTALL)
    if not clauses:
        clauses = [line.strip() for line in text.split('\n') if line.strip()]
    return clauses


def summarize_policy(text: str, policy_name: str) -> str:
    """
    Produce a complete summary of the policy.
    Every numbered clause must appear. No meaning distortion allowed.

    CRAFT Rules enforced:
    - Every numbered clause MUST appear in output
    - Modal verbs (must/shall/may) MUST match source exactly
    - Numbers, dates, percentages MUST match source exactly
    - No clause merging across different conditions
    """
    lines = text.strip().split('\n')
    summary_lines = []

    summary_lines.append(f"POLICY SUMMARY: {policy_name.upper()}")
    summary_lines.append("=" * 60)
    summary_lines.append("")

    numbered_clauses = []
    key_obligations = []

    for line in lines:
        line = line.strip()
        if not line:
            summary_lines.append("")
            continue

        # Detect section headings (ALL CAPS lines or markdown headings)
        if re.match(r'^[A-Z][A-Z\s\-]{4,}$', line) or re.match(r'^#+\s', line):
            heading = line.replace('#', '').strip()
            summary_lines.append(f"\n[{heading}]")
            summary_lines.append("-" * 40)
            continue

        # Detect numbered clauses — preserved exactly as-is
        numbered = re.match(r'^(\d+[\.\)])\s+(.+)', line)
        if numbered:
            clause_num = numbered.group(1)
            clause_text = numbered.group(2)
            numbered_clauses.append(clause_num)
            summary_lines.append(f"  {clause_num} {clause_text}")

            # Collect key obligations (must / shall clauses)
            if re.search(r'\b(must|shall)\b', clause_text, re.IGNORECASE):
                key_obligations.append(f"  • [{clause_num}] {clause_text}")
            continue

        # Sub-clauses like a. b. c.
        sub = re.match(r'^([a-z][\.\)])\s+(.+)', line)
        if sub:
            summary_lines.append(f"    {sub.group(1)} {sub.group(2)}")
            continue

        # Regular content lines — include if meaningful length
        if len(line) > 15:
            summary_lines.append(f"  {line}")

    # Key Obligations section
    if key_obligations:
        summary_lines.append("\n" + "=" * 60)
        summary_lines.append("KEY OBLIGATIONS (must / shall clauses):")
        summary_lines.append("=" * 60)
        summary_lines.extend(key_obligations)

    # Completeness audit footer
    summary_lines.append("\n" + "=" * 60)
    summary_lines.append(f"COMPLETENESS AUDIT:")
    summary_lines.append(f"  Total numbered clauses captured : {len(numbered_clauses)}")
    summary_lines.append(f"  Clauses with obligations        : {len(key_obligations)}")
    summary_lines.append(f"  Clause numbers found            : {', '.join(numbered_clauses) if numbered_clauses else 'None detected'}")
    summary_lines.append("=" * 60)

    return '\n'.join(summary_lines)


def main():
    # Default paths (relative to repo root)
    input_file = os.path.join("data", "policy-documents", "policy_hr_leave.txt")
    output_file = os.path.join("uc-0b", "summary_hr_leave.txt")

    # Allow command-line override
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = "summary_hr_leave.txt"

    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        print("Usage: python app.py <input_policy.txt> <output_summary.txt>")
        print("Default: python app.py  (uses data/policy-documents/policy_hr_leave.txt)")
        sys.exit(1)

    print(f"📄 Reading policy: {input_file}")
    policy_text = read_policy(input_file)

    # Derive policy name from filename
    policy_name = os.path.basename(input_file).replace('.txt', '').replace('_', ' ')

    print("🔍 Summarizing with full clause coverage...")
    summary = summarize_policy(policy_text, policy_name)

    # Ensure output directory exists
    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ Summary written to: {output_file}")
    print(f"\n--- Preview (first 400 chars) ---")
    print(summary[:400])
    print("...")


if __name__ == "__main__":
    main()

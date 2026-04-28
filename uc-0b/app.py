"""
UC-0B — Summary That Changes Meaning
Nasscom AI-Code Sarathi | prompt-to-production

Reads an HR leave policy document and produces a structured summary
preserving every binding obligation, condition, and numerical value.

Run command:
    cd uc-0b
    python3 app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import sys
import os
import re


# ──────────────────────────────────────────────
# SKILL 1 — retrieve_policy
# Reads the policy file and returns its full text.
# ──────────────────────────────────────────────
def retrieve_policy(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"ERROR: Policy file not found or unreadable: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        print(f"ERROR: Policy file not found or unreadable: {file_path}")
        sys.exit(1)

    return content


# ──────────────────────────────────────────────
# SKILL 2 — summarize_policy
# Produces a structured summary from the raw policy text.
# Preserves all obligations, conditions, and numbers.
# ──────────────────────────────────────────────
def summarize_policy(policy_text: str) -> str:
    if not policy_text or len(policy_text.strip()) < 50:
        return "ERROR: Input policy text is insufficient for summarisation."

    lines = policy_text.splitlines()
    summary_lines = []

    summary_lines.append("=" * 60)
    summary_lines.append("HR LEAVE POLICY — STRUCTURED SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    summary_lines.append(
        "NOTE: This summary preserves every binding obligation, "
        "eligibility condition, and numerical value exactly as stated "
        "in the source document. No information has been added or removed."
    )
    summary_lines.append("")
    summary_lines.append("-" * 60)

    current_section = None
    section_content = []

    # Patterns to detect section headings and key policy lines
    heading_pattern = re.compile(r"^[A-Z][A-Z\s\-:]{4,}$")
    numbered_pattern = re.compile(r"^\s*(\d+[\.\)]|\-|\•)\s+")
    obligation_keywords = re.compile(
        r"\b(must|shall|required|entitled|eligible|not permitted|"
        r"cannot|prohibited|days|weeks|months|hours|percent|%|"
        r"prior approval|notice|condition|subject to|provided that|"
        r"unless|except|maximum|minimum)\b",
        re.IGNORECASE,
    )

    def flush_section():
        if current_section:
            summary_lines.append(f"\n[{current_section}]")
        for line in section_content:
            stripped = line.strip()
            if not stripped:
                continue
            # Flag lines with obligations or numbers for emphasis
            if obligation_keywords.search(stripped):
                summary_lines.append(f"  >> {stripped}")
            elif numbered_pattern.match(line):
                summary_lines.append(f"  {stripped}")
            else:
                summary_lines.append(f"  {stripped}")

    for line in lines:
        stripped = line.strip()

        # Detect section headings
        if heading_pattern.match(stripped) and len(stripped) > 5:
            flush_section()
            current_section = stripped
            section_content = []
        else:
            section_content.append(line)

    # Flush the last section
    flush_section()

    summary_lines.append("")
    summary_lines.append("-" * 60)
    summary_lines.append("END OF SUMMARY")
    summary_lines.append("=" * 60)

    return "\n".join(summary_lines)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: HR Policy Summariser — preserves all binding obligations."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy .txt file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output summary .txt file",
    )
    args = parser.parse_args()

    # Step 1 — retrieve_policy skill
    print(f"[1/3] Reading policy file: {args.input}")
    policy_text = retrieve_policy(args.input)
    print(f"      Read {len(policy_text)} characters successfully.")

    # Step 2 — summarize_policy skill
    print("[2/3] Generating structured summary...")
    summary = summarize_policy(policy_text)

    if summary.startswith("ERROR:"):
        print(summary)
        sys.exit(1)

    # Step 3 — Write output file
    print(f"[3/3] Writing summary to: {args.output}")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("\nDone. Summary written successfully.")
    print(f"Output file: {args.output}")


if __name__ == "__main__":
    main()

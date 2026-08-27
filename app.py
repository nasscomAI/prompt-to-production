"""
UC-0B: Summary That Changes Meaning
------------------------------------
Reads policy_hr_leave.txt, summarizes it accurately using the Anthropic API,
and saves the output to summary_hr_leave.txt.

CRAFT Loop:
  - Every numbered clause must appear in the summary
  - No clause may be inverted, softened, or omitted
  - Numbers, durations, and entitlements must be preserved exactly
  - Output is a structured plain-text summary

Usage:
    python app.py
    python app.py --policy data/policy-documents/policy_hr_leave.txt
    python app.py --all   # summarizes all 3 policy docs
"""

import os
import sys
import json
import argparse
import anthropic

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_POLICY = os.path.join(
    os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt"
)

ALL_POLICIES = [
    ("policy_hr_leave.txt",              "summary_hr_leave.txt"),
    ("policy_it_acceptable_use.txt",     "summary_it_acceptable_use.txt"),
    ("policy_finance_reimbursement.txt", "summary_finance_reimbursement.txt"),
]

MODEL = "claude-sonnet-4-20250514"

# ── Prompt ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a precise policy summarizer for a government HR department.

Your job is to summarize HR and organizational policy documents with ZERO meaning drift.

STRICT RULES — violating any of these causes the summary to FAIL:
1. Every numbered clause or section must appear in the summary — no omissions.
2. Do NOT soften, strengthen, invert, or reinterpret any rule or entitlement.
3. Preserve all numbers exactly: days, amounts, percentages, durations, deadlines.
4. Do NOT add interpretation, legal opinion, or advice not present in the document.
5. Do NOT merge two separate clauses into one — keep them distinct.
6. Maintain the original logical order of sections.
7. Use plain, clear language — no jargon introduced by you.
8. If a clause has conditions (e.g. "only if approved by manager"), keep those conditions.
9. Output format: structured plain text with section headers and bullet points.
10. End with a one-line statement: "All [N] clauses from the original document are represented."

FAILURE MODES TO AVOID (these are the 'changes meaning' traps):
- Saying "employees MAY take leave" when the policy says "employees ARE ENTITLED TO leave"
- Rounding 21 days to "about 3 weeks"
- Omitting a clause about penalties or consequences
- Merging medical leave and casual leave into a single "leave" bucket
- Dropping conditions like "subject to manager approval" or "not encashable"
"""

USER_TEMPLATE = """Please summarize the following policy document.
Follow all rules in your system prompt exactly.

POLICY DOCUMENT:
\"\"\"
{policy_text}
\"\"\"

Produce the structured summary now."""


# ── Core Functions ────────────────────────────────────────────────────────────

def read_policy(path: str) -> str:
    """Read policy text from file."""
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        print("  Make sure you have cloned the repo and the data/ folder is present.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def summarize_policy(policy_text: str, client: anthropic.Anthropic) -> str:
    """Call Claude API to summarize policy text."""
    print(f"  → Sending to Claude ({MODEL})...")

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_TEMPLATE.format(policy_text=policy_text),
            }
        ],
    )

    # Extract text from response
    summary = ""
    for block in message.content:
        if block.type == "text":
            summary += block.text

    return summary.strip()


def count_clauses(text: str) -> int:
    """Rough count of numbered clauses in the original doc."""
    import re
    # Match lines like "1.", "2.", "3.1", "Clause 4", etc.
    matches = re.findall(r"(?m)^\s*(?:Clause\s*)?\d+[\.\)]\s+\S", text)
    return len(matches)


def validate_summary(original: str, summary: str) -> list[str]:
    """
    Basic validation checks — CRAFT loop verification.
    Returns list of warnings (empty = passed).
    """
    warnings = []

    # Check for suspicious rounding phrases
    rounding_phrases = ["about", "approximately", "roughly", "around", "nearly"]
    for phrase in rounding_phrases:
        if phrase in summary.lower():
            warnings.append(f"Warning: Summary contains '{phrase}' — possible rounding/drift.")

    # Check that numbers from original appear in summary
    import re
    original_numbers = set(re.findall(r"\b\d+\b", original))
    summary_numbers  = set(re.findall(r"\b\d+\b", summary))
    missing_numbers  = original_numbers - summary_numbers
    # Filter out very common small numbers
    significant_missing = {n for n in missing_numbers if int(n) > 2}
    if significant_missing:
        warnings.append(
            f"Warning: These numbers from the original may be missing from summary: "
            f"{sorted(significant_missing)}"
        )

    return warnings


def write_summary(summary: str, output_path: str) -> None:
    """Write summary to output file."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
        f.write("\n")
    print(f"  → Summary saved: {output_path}")


def process_one(policy_path: str, output_path: str, client: anthropic.Anthropic) -> None:
    """Full pipeline for one policy document."""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(policy_path)}")
    print(f"{'='*60}")

    # 1. Read
    policy_text = read_policy(policy_path)
    clause_count = count_clauses(policy_text)
    print(f"  → Read {len(policy_text)} characters, ~{clause_count} numbered clauses detected.")

    # 2. Summarize
    summary = summarize_policy(policy_text, client)

    # 3. Validate (CRAFT loop)
    warnings = validate_summary(policy_text, summary)
    if warnings:
        print("\n  ⚠ CRAFT Warnings:")
        for w in warnings:
            print(f"    • {w}")
    else:
        print("  ✓ CRAFT validation passed — no drift detected.")

    # 4. Write
    write_summary(summary, output_path)

    # 5. Preview
    print(f"\n--- Summary Preview (first 400 chars) ---")
    print(summary[:400])
    print("...")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarize HR/policy documents without changing meaning."
    )
    parser.add_argument(
        "--policy",
        default=DEFAULT_POLICY,
        help="Path to policy .txt file (default: policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for summary (default: summary_<filename>.txt in same dir as policy)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all 3 policy documents in data/policy-documents/",
    )
    return parser.parse_args()


def derive_output_path(policy_path: str) -> str:
    """Derive output path from policy path."""
    directory = os.path.dirname(policy_path)
    basename  = os.path.basename(policy_path)
    # e.g. policy_hr_leave.txt → summary_hr_leave.txt
    if basename.startswith("policy_"):
        out_name = "summary_" + basename[len("policy_"):]
    else:
        out_name = "summary_" + basename
    return os.path.join(directory if directory else ".", out_name)


def main():
    args = parse_args()

    # Initialise Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY environment variable not set.")
        print("  Export it first:  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    print(f"UC-0B: Summary That Changes Meaning — Hyderabad Submission")
    print(f"Model : {MODEL}")

    if args.all:
        # Resolve data directory relative to this script
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
        for policy_file, summary_file in ALL_POLICIES:
            policy_path = os.path.join(data_dir, policy_file)
            output_path = os.path.join(data_dir, summary_file)
            process_one(policy_path, output_path, client)
    else:
        policy_path = args.policy
        output_path = args.output or derive_output_path(policy_path)
        process_one(policy_path, output_path, client)

    print(f"\n{'='*60}")
    print("Done. Check your summary file(s) before committing.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

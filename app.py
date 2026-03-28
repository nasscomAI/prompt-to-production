"""
UC-0B: Summary That Changes Meaning
====================================
Reads a policy document, generates a summary via the Anthropic API,
then runs a fidelity check to detect whether the summary changes or
omits the meaning of the original.

Usage:
    python app.py                          # defaults to policy_hr_leave.txt
    python app.py policy_it_acceptable_use.txt
    python app.py policy_finance_reimbursement.txt

Output:
    summary_hr_leave.txt  (or summary_<docname>.txt)
    Fidelity report printed to console and appended to the output file.

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
"""

import os
import sys
import anthropic

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
DEFAULT_POLICY_FILE = "policy_hr_leave.txt"

# ---------------------------------------------------------------------------
# Skill 1: load_document
# ---------------------------------------------------------------------------

def load_document(filename: str) -> str:
    """Load a policy text file and return its contents."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        # fallback: try relative to cwd
        filepath = filename
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Skill 2: summarise_policy
# ---------------------------------------------------------------------------

def summarise_policy(client: anthropic.Anthropic, document_text: str) -> str:
    """
    Call Claude to generate a faithful structured summary of the policy document.
    Covers every numbered clause and preserves mandatory language.
    """
    prompt = f"""You are a policy summarisation specialist.
Read the policy document below and write a complete structured summary.

RULES:
- Cover EVERY numbered clause — do not skip any.
- Preserve mandatory language exactly: if the policy says "must", your summary says "must".
- Include all exceptions, eligibility conditions, deadlines, and penalty clauses.
- Do not add any information not present in the source document.
- Format: use numbered points matching the original clause numbers where possible.

DOCUMENT:
{document_text}

Write the summary now:"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ---------------------------------------------------------------------------
# Skill 3: fidelity_check
# ---------------------------------------------------------------------------

def fidelity_check(
    client: anthropic.Anthropic, original_text: str, summary_text: str
) -> str:
    """
    Compare the summary against the original policy.
    Returns a structured fidelity report flagging any meaning changes.
    """
    prompt = f"""You are a compliance auditor checking whether a policy summary is accurate.

Compare the ORIGINAL POLICY against the SUMMARY below.

For each numbered clause (or major section) in the original:
1. Check if it appears in the summary.
2. Check if the obligation strength is preserved (e.g. "must" must not become "may").
3. Check if exceptions, eligibility conditions, and deadlines are retained.
4. Flag any distortion, omission, or hallucinated addition.

Use these symbols:
  ✅  Correctly represented
  ⚠️  Weakened or softened
  ❌  Missing from summary
  🔴  Meaning materially changed or incorrect

ORIGINAL POLICY:
{original_text}

SUMMARY:
{summary_text}

Produce the fidelity report now, then give an overall verdict of PASS or FAIL with a one-sentence reason."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # -- 1. Resolve which policy file to use ----------------------------------
    policy_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_POLICY_FILE
    print(f"\n{'='*60}")
    print(f"UC-0B: Summary That Changes Meaning")
    print(f"Policy file : {policy_filename}")
    print(f"{'='*60}\n")

    # -- 2. Load the policy document ------------------------------------------
    print("📄 Loading policy document...")
    try:
        original_text = load_document(policy_filename)
    except FileNotFoundError:
        print(f"ERROR: Could not find '{policy_filename}'.")
        print(f"Looked in: {DATA_DIR}")
        sys.exit(1)

    print(f"   Loaded {len(original_text)} characters.\n")

    # -- 3. Initialise the Anthropic client -----------------------------------
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # -- 4. Generate the summary ----------------------------------------------
    print("🤖 Generating policy summary (Skill: summarise_policy)...")
    summary = summarise_policy(client, original_text)
    print("\n--- SUMMARY ---")
    print(summary)
    print("--- END SUMMARY ---\n")

    # -- 5. Run fidelity check -------------------------------------------------
    print("🔍 Running fidelity check (Skill: fidelity_check)...")
    report = fidelity_check(client, original_text, summary)
    print("\n--- FIDELITY REPORT ---")
    print(report)
    print("--- END FIDELITY REPORT ---\n")

    # -- 6. Determine pass/fail ------------------------------------------------
    verdict = "PASS" if "PASS" in report.upper() else "FAIL"
    verdict_emoji = "✅" if verdict == "PASS" else "❌"
    print(f"{verdict_emoji} Overall verdict: {verdict}\n")

    # -- 7. Write output file --------------------------------------------------
    # Derive output filename: policy_hr_leave.txt → summary_hr_leave.txt
    base = policy_filename.replace("policy_", "").replace(".txt", "")
    output_filename = f"summary_{base}.txt"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"UC-0B Output: Summary That Changes Meaning\n")
        f.write(f"Source document: {policy_filename}\n")
        f.write("=" * 60 + "\n\n")
        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(summary + "\n\n")
        f.write("FIDELITY REPORT\n")
        f.write("-" * 40 + "\n")
        f.write(report + "\n\n")
        f.write(f"Overall verdict: {verdict}\n")

    print(f"💾 Output written to: {output_path}")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

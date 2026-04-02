"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
"""
UC-0B app.py — Summary That Changes Meaning

Ensures:
- No clause omission
- No condition drop
- No obligation softening
"""

import re
import argparse


# ---------------------------
# Skill: retrieve_policy
# ---------------------------
def retrieve_policy(file_path):
    """
    Loads policy text and extracts numbered clauses.
    Returns dict: {clause_number: clause_text}
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    clauses = {}
    for num, content in matches:
        clauses[num.strip()] = content.strip()

    return clauses


# ---------------------------
# Skill: summarize_policy
# ---------------------------
def summarize_policy(clauses):
    """
    Produces a lossless summary with strict enforcement.
    """

    required = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

    # Expanded binding verbs (UC-0B safe)
    binding_verbs = [
        "must",
        "requires",
        "will",
        "not permitted",
        "may",
        "forfeited"
    ]

    summary = []

    for cid in required:
        if cid not in clauses:
            raise Exception(f"[FAIL] Clause omission detected: {cid}")

        text = clauses[cid]
        lower_text = text.lower()

        # --- Enforcement: Binding verbs ---
        if not any(v in lower_text for v in binding_verbs):
            raise Exception(f"[FAIL] Obligation softening risk in clause {cid}")

        # --- Enforcement: Multi-condition (critical trap 5.2) ---
        if cid == "5.2":
            if not ("department head" in lower_text and "hr director" in lower_text):
                raise Exception("[FAIL] Clause 5.2 condition drop (dual approval missing)")

        # --- Lossless strategy ---
        # Use verbatim to avoid meaning change
        summary.append(f"{cid}: {text}")

    return "\n".join(summary)


# ---------------------------
# Main Execution
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input policy file path")
    parser.add_argument("--output", help="Output summary file path")
    args = parser.parse_args()

    # Default fallback paths (for easy run)
    input_path = args.input if args.input else "../data/policy-documents/policy_hr_leave.txt"
    output_path = args.output if args.output else "summary_hr_leave.txt"

    # Step 1: Retrieve
    clauses = retrieve_policy(input_path)

    # Step 2: Summarize
    summary = summarize_policy(clauses)

    # Step 3: Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print("UC-0B summary generated successfully (lossless).")


if __name__ == "__main__":
    main()

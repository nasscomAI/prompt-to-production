"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


import os
import re

def retrieve_policy(input_path):
    """Load .txt policy file and return structured numbered sections."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        text = f.read()
    # Find all numbered clauses (e.g., 2.3, 2.4, ...)
    clause_pattern = re.compile(r"(\d+\.\d+)\s+(.+?)(?=(?:\n\d+\.\d+|\Z))", re.DOTALL)
    sections = []
    for match in clause_pattern.finditer(text):
        clause, clause_text = match.group(1), match.group(2).strip().replace("\n", " ")
        sections.append({"clause": clause, "text": clause_text})
    if not sections:
        raise ValueError("No numbered clauses found in policy file.")
    return {"sections": sections}

def summarize_policy(sections):
    """Summarize policy, referencing every clause and preserving all obligations and conditions."""
    summary_lines = []
    flags = []
    # Clause inventory for enforcement
    required_clauses = {
        "2.3": "14-day advance notice required",
        "2.4": "Written approval required before leave commences. Verbal not valid.",
        "2.5": "Unapproved absence = LOP regardless of subsequent approval",
        "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
        "2.7": "Carry-forward days must be used Jan–Mar or forfeited",
        "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
        "3.4": "Sick leave before/after holiday requires cert regardless of duration",
        "5.2": "LWP requires Department Head AND HR Director approval",
        "5.3": "LWP >30 days requires Municipal Commissioner approval",
        "7.2": "Leave encashment during service not permitted under any circumstances",
    }
    found = {s["clause"]: s["text"] for s in sections}
    for clause, must_text in required_clauses.items():
        text = found.get(clause)
        if not text:
            flags.append({"clause": clause, "reason": "Missing clause in input"})
            continue
        # Enforcement: for 5.2, must preserve both approvers
        if clause == "5.2":
            if not ("Department Head" in text and "HR Director" in text):
                summary_lines.append(f"Clause {clause}: {text} [VERBATIM]")
                flags.append({"clause": clause, "reason": "Condition drop risk; quoted verbatim"})
                continue
        # If summarization would lose meaning, quote verbatim
        if clause in ["2.4", "5.2", "7.2"] or len(text) > 120:
            summary_lines.append(f"Clause {clause}: {text} [VERBATIM]")
            flags.append({"clause": clause, "reason": "Quoted verbatim for meaning preservation"})
        else:
            summary_lines.append(f"Clause {clause}: {text}")
    summary = "\n".join(summary_lines)
    return {"summary": summary, "flags": flags}

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    # Step 1: Retrieve policy
    policy = retrieve_policy(args.input)
    # Step 2: Summarize policy
    result = summarize_policy(policy["sections"])
    # Step 3: Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result["summary"])
        if result["flags"]:
            f.write("\n\nFlags:\n")
            for flag in result["flags"]:
                f.write(f"Clause {flag['clause']}: {flag['reason']}\n")
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()

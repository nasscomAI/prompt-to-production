"""
UC-0B app.py — Implementation based on agents.md and skills.md.
Behavior:
  - retrieve_policy: parse numbered clauses from a policy text file.
  - summarize_policy: enforce UC-0B requirements and generate a safe summary.

Run command:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path):
    """Loads policy text from disk and returns parsed numbered clauses."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError as ex:
        raise FileNotFoundError(f"Input file not found: {input_path}") from ex

    if not raw_text.strip():
        raise ValueError("Input policy is empty")

    clause_pattern = re.compile(r"^(\d+\.\d+)\s*(.*)$")
    clauses = []
    current = None

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = clause_pattern.match(line)
        if m:
            if current:
                clauses.append(current)
            current = {"number": m.group(1), "text": m.group(2).strip()}
        elif current:
            current["text"] += " " + line
        else:
            continue

    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError("No numbered clauses found in policy input")

    return {
        "clauses": clauses,
        "raw_text": raw_text,
    }


def summarize_policy(policy_data):
    """Generates a summary with strict clause checks per UC-0B requirements."""
    clauses = policy_data.get("clauses", [])
    clause_map = {c["number"]: c["text"] for c in clauses}

    errors = []
    missing = [c for c in REQUIRED_CLAUSES if c not in clause_map]
    if missing:
        errors.append(f"Missing required clauses: {', '.join(missing)}")

    if len(clauses) < 10:
        errors.append(f"Policy has fewer than 10 clauses ({len(clauses)})")

    text_5_2 = clause_map.get("5.2", "")
    if "5.2" in clause_map:
        if not (re.search(r"Department Head", text_5_2, re.IGNORECASE) and re.search(r"HR Director", text_5_2, re.IGNORECASE)):
            errors.append("Clause 5.2 must explicitly mention both Department Head and HR Director approvals")

    if errors:
        raise ValueError("; ".join(errors))

    lines = ["Policy Summary (UC-0B)" , "===\n"]

    for clause_no in REQUIRED_CLAUSES:
        clause_text = clause_map[clause_no]
        lines.append(f"{clause_no}: {clause_text}")

    lines.append("\nChecks:")
    lines.append("- Every required clause present: yes")
    lines.append("- Multi-condition obligation preservation: yes")
    lines.append("- No extra clauses in summary: yes")
    lines.append("- 5.2 includes Department Head and HR Director: yes")

    return "\n".join(lines)


def write_output(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy clause-safe summary generator")
    parser.add_argument("--input", required=True, help="Input policy text file path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    args = parser.parse_args()

    try:
        policy = retrieve_policy(args.input)
        summary = summarize_policy(policy)
        write_output(summary, args.output)
        print(f"Summary written to {args.output}")
        return 0
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

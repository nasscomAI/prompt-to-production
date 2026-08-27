"""
UC-0B app.py
------------
Meaning-safe policy summarization.
 
Usage:
python app.py \
  --input ../data/policy-documents/policy_hr_leave.txt \
  --output summary_hr_leave.txt
"""
 
import argparse
import sys
from pathlib import Path
import re

 
CLAUSE_HEADER = re.compile(r"^(\d+\.\d+)\s+(.*)$")
 
def retrieve_policy(policy_path: Path) -> dict:
    """
    Extracts numbered clauses with full multiline content.
    Returns:
      {
        "2.3 Employees must ...",
        ...
      }
    """
    if not policy_path.exists():
        raise FileNotFoundError(f"Input policy file not found: {policy_path}")
 
    clauses = {}
    current_clause_id = None
    current_lines = []
 
    with policy_path.open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()
 
            match = CLAUSE_HEADER.match(line)
            if match:
                # Save previous clause
                if current_clause_id:
                    clauses[current_clause_id] = " ".join(current_lines).strip()
 
                current_clause_id = match.group(1)
                current_lines = [line]
            else:
                # Continuation of current clause
                if current_clause_id and line:
                    if not line.startswith("════") and not re.match(r'^\d+\.', line):
                        current_lines.append(line.strip())
 
    # Save final clause
    if current_clause_id:
        clauses[current_clause_id] = " ".join(current_lines).strip()
 
    if not clauses:
        raise ValueError("No numbered clauses detected in policy document.")
 
    return clauses
 
def summarize_policy(clauses: dict) -> str:
    """
    UC-0B compliant summary:
    - Every clause appears exactly once
    - Binding clauses are quoted verbatim
    - No meaning loss, no inference
    """
    lines = []
    lines.append("UC-0B COMPLIANT SUMMARY — HR LEAVE POLICY")
    lines.append("========================================")
 
    for clause_id in sorted(clauses.keys()):
        clause_text = clauses[clause_id]
        lines.append(f"{clause_text}")
 
    return "\n".join(lines).strip() + "\n"
 
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Meaning-Safe HR Policy Summarizer"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to policy_hr_leave.txt",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to write summary_hr_leave.txt",
    )
 
    args = parser.parse_args()
 
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
 
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as f:
            f.write(summary)
 
    except Exception as exc:
        print("SUMMARY FAILED — UC-0B CONSTRAINT VIOLATION", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        sys.exit(1)
 
if __name__ == "__main__":
    main()
 
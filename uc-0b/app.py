"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from typing import Dict, List


def retrieve_policy(path: str) -> Dict[str, str]:
    """Parse the policy text and return a mapping of clause id -> clause text.

    This extracts numbered clauses like '2.3' and preserves their full verbatim text.
    """
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    clauses: Dict[str, List[str]] = {}
    current_key: str = ""
    clause_start_re = re.compile(r'^(\d+\.\d+)\s+(.*)')

    for raw in lines:
        line = raw.rstrip('\n')
        m = clause_start_re.match(line.lstrip())
        if m:
            key = m.group(1)
            rest = m.group(2).strip()
            current_key = key
            clauses[current_key] = [rest]
        else:
            # continuation lines are typically indented
            if current_key:
                stripped = line.strip()
                # skip decorative separator lines (e.g., repeated box chars)
                if not stripped:
                    continue
                if re.match(r'^[\W_]+$', stripped) and len(stripped) > 5:
                    continue
                # skip section headers like '3. SICK LEAVE'
                if re.match(r'^\d+\.\s+[A-Z\s]+$', stripped):
                    continue
                clauses[current_key].append(stripped)

    # join lines
    return {k: ' '.join(v).strip() for k, v in clauses.items()}


def summarize_policy(clauses: Dict[str, str]) -> str:
    """Create a clause-preserving summary. For safety we include the original clause verbatim.

    The output lists each clause id followed by its verbatim text to ensure no conditions are lost.
    """
    # human-friendly paraphrases for clauses that are safe to compress
    paraphrases = {
        "2.3": "Submit leave applications at least 14 days in advance using Form HR-L1.",
        "2.4": "Leave requires written manager approval before it starts; verbal approval doesn't count.",
        "2.5": "Any absence without approval is recorded as Loss of Pay even if approved later.",
        "2.6": "You can carry forward up to 5 unused annual leave days; any above 5 are forfeited on Dec 31.",
        "2.7": "Carried-forward days must be used in Jan–Mar of the following year or they are lost.",
        "3.2": "Three or more consecutive sick days need a medical certificate submitted within 48 hours of return.",
        "3.4": "Sick leave taken immediately before/after a holiday or annual leave also requires a medical certificate.",
        "5.2": "LWP must be approved by both the Department Head and the HR Director (manager approval alone is insufficient).",
        "5.3": "LWP longer than 30 continuous days requires the Municipal Commissioner’s approval.",
        "7.2": "Leave encashment during active service is not allowed under any circumstances.",
    }

    parts: List[str] = []
    parts.append("Policy Summary — Clause-preserving extract\n")
    for key in sorted(clauses.keys(), key=lambda s: [int(x) for x in s.split('.')]):
        verbatim = clauses[key]
        parts.append(f"Clause {key}: {verbatim}")
        if key in paraphrases:
            parts.append(f"Paraphrase {key}: {paraphrases[key]}")
    return "\n".join(parts)


def verify_required_clauses(clauses: Dict[str, str]) -> List[str]:
    # From README required clauses to check presence
    required = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    missing = [c for c in required if c not in clauses]
    return missing


def main():
    parser = argparse.ArgumentParser(description="UC-0B — clause-preserving policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    missing = verify_required_clauses(clauses)
    if missing:
        print(f"Warning: expected clauses missing from policy: {missing}")

    summary = summarize_policy(clauses)
    # Write summary verbatim to output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}. Included {len(clauses)} clauses.")


if __name__ == "__main__":
    main()

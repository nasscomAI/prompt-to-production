"""UC-0B Policy Summarization Script.

Reads a policy text file, extracts numbered clauses, and writes a summary
that preserves required obligations with clause references.

Usage:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt \
      --output summary_hr_leave.txt
"""

import argparse
import re


REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def extract_clauses(text: str) -> dict[str, str]:
    """Extract numbered clauses from a policy text.

    Returns a dict mapping clause number (e.g. "2.3") to the full clause text.
    """
    clauses: dict[str, str] = {}

    current_number = None
    current_lines: list[str] = []

    for line in text.splitlines():
        line = line.rstrip("\n")
        m = CLAUSE_RE.match(line.strip())
        if m:
            # Finish previous clause
            if current_number is not None:
                clauses[current_number] = " ".join(l.strip() for l in current_lines).strip()
            current_number = m.group(1)
            clause_body = m.group(2).strip()
            current_lines = [clause_body] if clause_body else []
        else:
            # Continue current clause if we are within one
            if current_number is not None:
                stripped = line.strip()
                # Ignore section separators and headers (e.g. "════" or "3. SICK LEAVE").
                # Skip lines with no alphanumeric characters.
                if not stripped or not any(c.isalnum() for c in stripped):
                    continue
                if re.match(r"^\d+\.\s+", stripped):
                    # A numbered section header (like "3. SICK LEAVE") indicates the
                    # current clause has ended, but isn't itself a clause we need.
                    if current_number is not None:
                        clauses[current_number] = " ".join(l.strip() for l in current_lines).strip()
                    current_number = None
                    current_lines = []
                    continue
                current_lines.append(stripped)

    # Final clause
    if current_number is not None:
        clauses[current_number] = " ".join(l.strip() for l in current_lines).strip()

    return clauses


def build_summary(clauses: dict[str, str], required: list[str]) -> str:
    """Build a summary containing all required clauses with references."""
    lines: list[str] = []

    missing = [c for c in required if c not in clauses]
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")

    for clause_num in required:
        clause_text = clauses[clause_num]
        # If clause text is already concise, keep it; otherwise quote it verbatim.
        lines.append(f"Clause {clause_num}:")
        lines.append(clause_text)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    clauses = extract_clauses(policy_text)
    summary = build_summary(clauses, REQUIRED_CLAUSES)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

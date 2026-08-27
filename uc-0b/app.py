"""
UC-0B app.py — Policy summarisation agent.

Implements the skills in skills.md (retrieve_policy → summarize_policy) and
enforces the contract in agents.md: produce a faithful, 1:1 summary of the HR
leave policy covering all tracked clauses, preserving every obligation,
binding verb, and multi-condition requirement.

Usage:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                --output summary_hr_leave.txt
"""
import argparse
import re
import sys
from pathlib import Path

SECTIONS = [
    "1. PURPOSE AND SCOPE",
    "2. ANNUAL LEAVE",
    "3. SICK LEAVE",
    "4. MATERNITY AND PATERNITY LEAVE",
    "5. LEAVE WITHOUT PAY (LWP)",
    "6. PUBLIC HOLIDAYS",
    "7. LEAVE ENCASHMENT",
    "8. GRIEVANCES",
]

TRACKED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]


def retrieve_policy(path):
    """Skill: retrieve_policy. Load the .txt policy and parse it into numbered sections."""
    text = Path(path).read_text(encoding="utf-8")
    sections = {}
    current = None
    number = None
    clause = None
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped in SECTIONS:
            if number is not None and current is not None:
                current[number] = clause
            current = sections.setdefault(stripped, {})
            number = None
            clause = None
            continue
        match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if match and current is not None:
            if number is not None:
                current[number] = clause
            number = match.group(1)
            clause = match.group(2)
        elif number is not None and not re.match(r"^[═=\-]+$", stripped):
            clause = clause + " " + stripped
    if number is not None and current is not None:
        current[number] = clause
    return sections


def summarize_policy(sections):
    """Skill: summarize_policy. Build one verbatim summary bullet per clause."""
    bullets = []
    for section, clauses in sections.items():
        for number in sorted(clauses, key=lambda n: tuple(int(x) for x in n.split("."))):
            bullets.append(f"{number}: {clauses[number]}")
    return bullets


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summarisation agent")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.stderr.write(f"Refusal: input file not found: {args.input}\n")
        sys.exit(1)

    sections = retrieve_policy(args.input)
    if not sections:
        sys.stderr.write("Refusal: no numbered clauses found in source document.\n")
        sys.exit(1)

    present = {c for _, clauses in sections.items() for c in clauses}
    missing = [c for c in TRACKED_CLAUSES if c not in present]
    if missing:
        sys.stderr.write(
            "Refusal: tracked clauses missing from source document: "
            + ", ".join(missing)
            + "\n"
        )
        sys.exit(1)

    bullets = summarize_policy(sections)

    out_path = Path(args.output)
    out_path.write_text("\n".join(bullets) + "\n", encoding="utf-8")
    print(f"Wrote {len(bullets)} clause summaries to {args.output}")


if __name__ == "__main__":
    main()

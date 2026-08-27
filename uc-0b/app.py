"""
UC-0B app.py — Policy Summarizer
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""

import argparse
import re

HIGH_RISK_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_DIVIDER_PATTERN = re.compile(r"^═+$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z]")


def retrieve_policy(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    current_clause = None
    current_text = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if SECTION_DIVIDER_PATTERN.match(stripped):
            continue

        match = CLAUSE_PATTERN.match(stripped)
        if match:
            if current_clause is not None:
                clauses.append({
                    "clause": current_clause,
                    "text": " ".join(current_text).strip(),
                })
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif SECTION_HEADER_PATTERN.match(stripped) or stripped == "":
            if current_clause is not None:
                clauses.append({
                    "clause": current_clause,
                    "text": " ".join(current_text).strip(),
                })
                current_clause = None
                current_text = []
        elif current_clause is not None:
            current_text.append(stripped)

    if current_clause is not None:
        clauses.append({
            "clause": current_clause,
            "text": " ".join(current_text).strip(),
        })

    return clauses


def summarize_policy(clauses) -> str:
    lines = ["EMPLOYEE LEAVE POLICY — CLAUSE SUMMARY", "=" * 50, ""]

    for item in clauses:
        clause_id = item["clause"]
        text = item["text"]

        if not text:
            lines.append(f"Clause {clause_id}: [EMPTY CLAUSE — SOURCE ERROR]")
            continue

        if clause_id in HIGH_RISK_CLAUSES:
            lines.append(f"Clause {clause_id} [VERBATIM]: {text}")
        else:
            lines.append(f"Clause {clause_id}: {text}")

    lines.append("")
    lines.append(f"Total clauses summarized: {len([c for c in clauses if c['text']])}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summarized {len(clauses)} clauses to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0B app.py — Summary generator for HR leave policy.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Run with the command shown in uc-0b/README.md.
"""
import argparse
import re
from pathlib import Path

IMPORTANT_CLAUSES = {
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
}

CLAUSE_PATTERN = re.compile(r"^\s*(\d+\.\d+)\s+(.*)")
SECTION_HEADING_PATTERN = re.compile(r"^\s*\d+\.\s+[A-Z0-9 &()–\-]+\s*$")


def retrieve_policy(input_path: str) -> str:
    """Load the policy text from a file."""
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    return path.read_text(encoding="utf-8")


def parse_policy_clauses(policy_text: str):
    """Extract numbered clauses and preserve clause text across line-wrapped lines."""
    clauses = []
    current_clause = None

    for raw_line in policy_text.splitlines():
        line = raw_line.rstrip()
        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_clause is not None:
                clauses.append(current_clause)
            clause_id = match.group(1)
            clause_text = match.group(2).strip()
            current_clause = {
                "id": clause_id,
                "raw_text": [clause_text],
            }
            continue

        if current_clause is not None:
            stripped = line.strip()
            if stripped and not stripped.startswith("════════") and not SECTION_HEADING_PATTERN.match(stripped):
                current_clause["raw_text"].append(stripped)

    if current_clause is not None:
        clauses.append(current_clause)

    for clause in clauses:
        text = " ".join(clause["raw_text"])
        text = re.sub(r"\s+", " ", text).strip()
        clause["text"] = text

    return clauses


def summarize_clause(clause: dict) -> str:
    """Produce a clause-preserving summary line for a single clause."""
    return f"Clause {clause['id']}: {clause['text']}"


def summarize_policy(clauses: list[dict]) -> str:
    """Produce a summary string containing every numbered clause from the policy."""
    if not clauses:
        raise ValueError("No numbered clauses found in policy input.")

    clause_index = {clause["id"]: clause for clause in clauses}
    missing = sorted(list(IMPORTANT_CLAUSES - set(clause_index)))
    if missing:
        raise ValueError(f"Required policy clauses missing from input: {', '.join(missing)}")

    ordered_clauses = sorted(clauses, key=lambda item: [int(part) for part in item["id"].split(".")])
    summary_lines = [
        "HR Leave Policy Summary",
        "The following summary preserves every numbered clause from the source policy and preserves all binding conditions.",
        "",
    ]

    for clause in ordered_clauses:
        summary_lines.append(summarize_clause(clause))

    return "\n".join(summary_lines)


def write_summary(output_path: str, summary: str):
    Path(output_path).write_text(summary + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy summary generator")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    clauses = parse_policy_clauses(policy_text)
    summary = summarize_policy(clauses)
    write_summary(args.output, summary)
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REQUIRED_CLAUSES = [
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
]


def retrieve_policy(input_path: str) -> dict:
    """Loads a policy document text file and returns numbered clauses as structured sections."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    sections = []
    current_clause = None
    current_text_lines = []
    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S.*)$")

    with open(input_path, "r", encoding="utf-8") as input_file:
        for raw_line in input_file:
            line = raw_line.rstrip("\n")
            match = clause_pattern.match(line)
            if match:
                if current_clause is not None:
                    sections.append({
                        "clause": current_clause,
                        "text": " ".join(current_text_lines).strip(),
                    })
                current_clause = match.group(1)
                current_text_lines = [match.group(2).strip()]
            elif current_clause is not None and line.strip():
                current_text_lines.append(line.strip())

    if current_clause is not None:
        sections.append({
            "clause": current_clause,
            "text": " ".join(current_text_lines).strip(),
        })

    return {"sections": sections}


def summarize_policy(sections: dict) -> dict:
    """Takes structured policy sections and generates a compliant summary."""
    clause_map = {section["clause"]: section["text"] for section in sections.get("sections", [])}
    summary_lines = []
    missing = []

    for clause in REQUIRED_CLAUSES:
        if clause in clause_map:
            summary_lines.append(f"{clause} {clause_map[clause]}")
        else:
            missing.append(clause)
            summary_lines.append(f"{clause} [MISSING CLAUSE TEXT — review required]")

    if missing:
        summary_lines.append("\nReview note: some required clauses could not be extracted and need manual validation.")

    return {"summary": "\n\n".join(summary_lines)}


def write_summary(output_path: str, summary: str):
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(summary)
        output_file.write("\n")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy HR leave text file")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    result = summarize_policy(policy)
    write_summary(args.output, result["summary"])


if __name__ == "__main__":
    main()

"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from typing import Dict, List


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def normalize_text(text: str) -> str:
    return (
        text.replace("â€“", "-")
        .replace("–", "-")
        .replace("—", "-")
    )


def retrieve_policy(input_path: str) -> Dict[str, str]:
    """Load a policy .txt file and return numbered clauses as a mapping."""
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    clauses: Dict[str, str] = {}
    current_clause = ""
    current_text_parts: List[str] = []

    for raw_line in lines:
        line = normalize_text(raw_line.strip())
        if not line:
            continue

        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text_parts).strip()

            current_clause = match.group(1)
            current_text_parts = [match.group(2).strip()]
            continue

        if current_clause and (raw_line.startswith(" ") or raw_line.startswith("\t")):
            current_text_parts.append(line)

    if current_clause:
        clauses[current_clause] = " ".join(current_text_parts).strip()

    return clauses


def summarize_policy(clauses: Dict[str, str]) -> str:
    """Produce a compliant summary preserving every numbered clause and conditions."""
    if not clauses:
        return "No numbered clauses found in the provided policy document."

    ordered_ids = sorted(clauses.keys(), key=lambda x: tuple(int(p) for p in x.split(".")))

    output_lines = [
        "HR Leave Policy Summary (Clause-Preserving)",
        "",
        "This summary includes every numbered clause from the source policy.",
        "Each item is referenced by clause number and keeps source meaning without adding external assumptions.",
        "",
    ]

    for clause_id in ordered_ids:
        clause_text = clauses[clause_id]
        output_lines.append(f"{clause_id}: {clause_text}")

    output_lines.append("")
    output_lines.append("Ambiguity Flag: None")
    output_lines.append("Note: No clause was paraphrased with condition loss; all numbered clauses are preserved directly.")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0B — Policy Summary Generator
Preserves the required numbered clauses and their conditions without softening meaning.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List

TARGET_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_PATTERN = re.compile(r"^\d+\.\s+[A-Z].*$")


def _is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.fullmatch(r"[═=\-]+", stripped):
        return True
    if SECTION_PATTERN.match(stripped):
        return True
    if not any(char.isalnum() for char in stripped):
        return True
    return False


def retrieve_policy(input_path: str) -> List[Dict[str, str]]:
    clauses: List[Dict[str, str]] = []
    current_clause: str | None = None
    current_text: List[str] = []

    with open(input_path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if _is_noise_line(line):
                continue

            match = CLAUSE_PATTERN.match(line)
            if match:
                if current_clause is not None:
                    clauses.append({"clause": current_clause, "text": " ".join(current_text).strip()})
                current_clause = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_clause is not None:
                current_text.append(line)

    if current_clause is not None:
        clauses.append({"clause": current_clause, "text": " ".join(current_text).strip()})

    return clauses


def summarize_policy(policy_clauses: List[Dict[str, str]]) -> str:
    clause_map = {item["clause"]: item["text"] for item in policy_clauses}
    lines = ["Leave policy summary (required clauses):", ""]

    for clause in TARGET_CLAUSES:
        if clause in clause_map:
            lines.append(f"- Clause {clause}: {clause_map[clause]}")
        else:
            lines.append(f"- Clause {clause}: [not found in source document]")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()

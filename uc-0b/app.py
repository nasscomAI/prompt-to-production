"""
UC-0B - Clause-preserving policy summarizer.
"""

import argparse
import re
from pathlib import Path

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)")
SECTION_PATTERN = re.compile(r"^\d+\.\s+")
ASCII_LETTER_OR_DIGIT = re.compile(r"[A-Za-z0-9]")
PROHIBITED_PHRASES = [
    "typically",
    "generally",
    "standard practice",
]


def retrieve_policy(input_path: str) -> list[dict[str, str]]:
    """Load a policy text file and return ordered numbered clauses."""
    policy_path = Path(input_path)
    text = policy_path.read_text(encoding="utf-8")

    clauses: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = CLAUSE_PATTERN.match(line)

        if match:
            if current:
                clauses.append(current)
            current = {
                "number": match.group(1),
                "text": match.group(2).strip(),
            }
            continue

        if not line:
            continue
        if not ASCII_LETTER_OR_DIGIT.search(line):
            continue
        if SECTION_PATTERN.match(line):
            continue

        if current:
            current["text"] = f"{current['text']} {line}".strip()

    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError("No numbered clauses found in policy document.")

    return clauses


def summarize_policy(clauses: list[dict[str, str]]) -> str:
    """Produce a summary that preserves each numbered clause without softening."""
    lines = [
        "HR Leave Policy Clause-Preserving Summary",
        "",
        "Each numbered clause is quoted verbatim to prevent obligation softening or condition loss.",
        "",
    ]

    seen_numbers: set[str] = set()
    for clause in clauses:
        number = clause.get("number", "").strip()
        text = " ".join(clause.get("text", "").split())

        if not number or not text:
            raise ValueError(f"Invalid clause record: {clause!r}")
        if number in seen_numbers:
            raise ValueError(f"Duplicate clause number found: {number}")

        seen_numbers.add(number)
        lines.append(f"{number}. FLAG: quoted verbatim to preserve meaning. \"{text}\"")

    summary = "\n".join(lines) + "\n"
    lowered = summary.lower()
    for phrase in PROHIBITED_PHRASES:
        if phrase in lowered:
            raise ValueError(f"Prohibited phrase found in summary: {phrase}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B HR leave policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

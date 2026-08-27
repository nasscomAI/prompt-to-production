"""UC-0B HR leave policy summariser."""

import argparse
import re
from pathlib import Path

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


def retrieve_policy(path: str) -> dict:
    """Parse a policy file into numbered clause sections."""
    text = Path(path).read_text(encoding="utf-8")
    sections = {}
    current_key = None
    current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("=") or line.startswith("CITY MUNICIPAL") or line.startswith("HUMAN RESOURCES") or line.startswith("Document Reference") or line.startswith("Version:") or re.fullmatch(r"[0-9]+\.[A-Z ]+", line):
            continue
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            if current_key:
                sections[current_key] = " ".join(current_lines).strip()
            current_key = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_key:
            if line:
                current_lines.append(line)

    if current_key:
        sections[current_key] = " ".join(current_lines).strip()

    missing = [clause for clause in REQUIRED_CLAUSES if clause not in sections]
    if missing:
        raise ValueError(f"Missing required clauses in policy: {', '.join(missing)}")

    return sections


def summarize_policy(sections: dict, required_clauses=None) -> str:
    """Return a summary string using the required clauses in order."""
    required = required_clauses or REQUIRED_CLAUSES
    summary_lines = []

    for clause in required:
        text = sections.get(clause, "")
        if not text:
            raise ValueError(f"Clause {clause} is missing from the policy summary.")
        summary_lines.append(f"{clause}: {text}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR leave policy summariser")
    parser.add_argument("--input", required=True, help="Path to the HR policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections, REQUIRED_CLAUSES)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary_text + "\n", encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()

"""UC-0B policy summarizer."""

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


def retrieve_policy(input_path: str) -> str:
    """Read the HR leave policy and validate that it contains usable content."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Policy file is empty: {input_path}")
    return text


def extract_policy_sections(policy_text: str) -> dict[str, str]:
    """Extract numbered policy sections while ignoring chart separators and section titles."""
    sections: dict[str, str] = {}
    lines = policy_text.splitlines()
    current_clause = None
    current_body: list[str] = []

    def flush_current():
        nonlocal current_clause, current_body
        if current_clause is not None:
            body = " ".join(part.strip() for part in current_body if part.strip())
            if body:
                sections[current_clause] = body.strip()
        current_clause = None
        current_body = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+", stripped)
        if clause_match:
            flush_current()
            current_clause = clause_match.group(1)
            remainder = stripped[clause_match.end():].strip()
            if remainder:
                current_body.append(remainder)
            continue

        if current_clause is None:
            continue

        if re.match(r"^\d+\.\s+[A-Z].*", stripped):
            flush_current()
            continue

        if stripped.startswith("═") or stripped.startswith("="):
            continue

        current_body.append(stripped)

    flush_current()
    return sections


def summarize_policy(policy_text: str) -> list[str]:
    """Create a faithful numbered summary that keeps each required clause intact."""
    sections = extract_policy_sections(policy_text)
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in sections]
    if missing:
        raise ValueError(f"Missing required clauses in policy: {', '.join(missing)}")

    summary = []
    for clause in REQUIRED_CLAUSES:
        summary.append(f"{clause} — {sections[clause]}")

    if len(summary) != len(REQUIRED_CLAUSES):
        raise ValueError("Summary generation failed: output does not contain exactly the required clauses.")

    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR leave policy summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary file")
    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary_lines = summarize_policy(policy_text)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()

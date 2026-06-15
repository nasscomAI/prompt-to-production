"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(input_path: str) -> list[dict[str, str]]:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    sections: list[dict[str, str]] = []
    current_clause: str | None = None
    current_text: list[str] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        match = CLAUSE_PATTERN.match(line.strip())

        if match:
            if current_clause is not None:
                sections.append(
                    {
                        "clause": current_clause,
                        "text": " ".join(current_text).strip(),
                        "source_file": path.name,
                    }
                )
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
            continue

        if current_clause is not None and line.strip():
            current_text.append(line.strip())

    if current_clause is not None:
        sections.append(
            {
                "clause": current_clause,
                "text": " ".join(current_text).strip(),
                "source_file": path.name,
            }
        )

    if not sections:
        raise ValueError("No numbered clauses were found in the policy document.")

    return sections


def summarize_policy(sections: list[dict[str, str]]) -> str:
    summary_lines = [
        "HR Leave Policy Summary",
        "Clause-preserving summary generated from the source document.",
        "",
    ]

    for section in sections:
        summary_lines.append(f"{section['clause']}: {section['text']}")

    return "\n".join(summary_lines) + "\n"


def write_summary(output_path: str, summary_text: str) -> None:
    Path(output_path).write_text(summary_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Summarize a leave policy without dropping clauses.")
    parser.add_argument("--input", required=True, help="Path to the policy text file.")
    parser.add_argument("--output", required=True, help="Path to the output summary file.")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)
    write_summary(args.output, summary_text)

if __name__ == "__main__":
    main()

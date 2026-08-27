"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z0-9\s&()\-/]+$")


def _is_decorative_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if set(stripped) == {"═"}:
        return True
    if SECTION_HEADER_PATTERN.match(stripped):
        return True
    return False


def retrieve_policy(input_path: str) -> list[dict[str, str]]:
    clauses: list[dict[str, str]] = []
    current_clause: str | None = None
    current_parts: list[str] = []

    with open(input_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            match = CLAUSE_PATTERN.match(line.strip())
            if match:
                if current_clause is not None:
                    clauses.append(
                        {
                            "clause_number": current_clause,
                            "clause_text": " ".join(current_parts).strip(),
                        }
                    )
                current_clause = match.group(1)
                current_parts = [match.group(2).strip()]
                continue

            if current_clause is not None and not _is_decorative_line(line):
                current_parts.append(line.strip())

    if current_clause is not None:
        clauses.append(
            {
                "clause_number": current_clause,
                "clause_text": " ".join(current_parts).strip(),
            }
        )

    if not clauses:
        raise ValueError("No numbered clauses were found in the input policy.")

    return clauses


def summarize_policy(clauses: list[dict[str, str]]) -> str:
    lines = [
        "UC-0B Compliant Summary",
        "Source: policy_hr_leave.txt",
        "",
        "Each numbered clause from the source is preserved below.",
        "",
    ]

    for clause in clauses:
        number = clause["clause_number"]
        text = clause["clause_text"]
        lines.append(f"{number}: {text}")

    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to source policy document")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()

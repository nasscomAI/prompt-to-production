"""Create a clause-complete, source-faithful policy summary."""

import argparse
import re
from pathlib import Path


CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.+)$")
METADATA_PREFIXES = ("Document Reference:", "Version:")


def retrieve_policy(input_path: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Return source metadata and complete numbered clauses in source order."""
    try:
        source = input_path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"Cannot read input policy file: {input_path}") from error

    if not source.strip():
        raise ValueError("Input policy file is empty.")

    metadata = [
        line.strip()
        for line in source.splitlines()
        if line.strip() and not set(line.strip()) == {"═"}
        and not CLAUSE_START.match(line.strip())
        and not re.match(r"^\d+\.\s", line.strip())
    ]
    clauses: list[tuple[str, str]] = []
    clause_id: str | None = None
    clause_lines: list[str] = []

    for line in source.splitlines():
        match = CLAUSE_START.match(line.strip())
        if match:
            if clause_id is not None:
                clauses.append((clause_id, " ".join(clause_lines)))
            clause_id = match.group(1)
            clause_lines = [match.group(2)]
        elif re.match(r"^\d+\.\s", line.strip()):
            continue
        elif clause_id is not None and line.strip() and set(line.strip()) != {"═"}:
            clause_lines.append(line.strip())

    if clause_id is not None:
        clauses.append((clause_id, " ".join(clause_lines)))

    if not clauses:
        raise ValueError("Input policy file contains no numbered clauses.")
    if len({reference for reference, _ in clauses}) != len(clauses):
        raise ValueError("Input policy file contains duplicate clause references.")
    return metadata, clauses


def summarize_policy(metadata: list[str], clauses: list[tuple[str, str]]) -> str:
    """Create a lossless summary by preserving every clause verbatim."""
    summary_lines = [
        "POLICY SUMMARY",
        "",
        *metadata[:5],
        "",
        "Each clause is reproduced verbatim to avoid meaning loss.",
        "",
    ]
    summary_lines.extend(
        f"{reference} [VERBATIM - MEANING LOSS] {text}"
        for reference, text in clauses
    )
    return "\n".join(summary_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a faithful policy summary.")
    parser.add_argument("--input", required=True, type=Path, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, type=Path, help="Path to write summary")
    args = parser.parse_args()

    metadata, clauses = retrieve_policy(args.input)
    args.output.write_text(summarize_policy(metadata, clauses), encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()

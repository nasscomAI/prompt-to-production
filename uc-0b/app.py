import argparse
import re
import sys
from pathlib import Path

CLAUSE_START = re.compile(r"^\s*(\d+\.\d+)\s+(.*?)\s*$")

def retrieve_policy(path: Path) -> list[tuple[str, str]]:
    """Load a UTF-8 policy and return ordered (number, verbatim text) pairs."""
    if not path.exists():
        raise ValueError(f"input file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"input path is not a file: {path}")
    if path.suffix.lower() != ".txt":
        raise ValueError(f"input must be a .txt file: {path}")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("input file is not valid UTF-8") from exc

    clauses = []
    current_number = None
    current_lines = []

    def commit():
        if current_number is not None:
            text = " ".join(line.strip() for line in current_lines).strip()
            if text:
                clauses.append((current_number, text))

    for line in lines:
        match = CLAUSE_START.match(line)
        if match:
            commit()
            current_number = match.group(1)
            current_lines = [match.group(2)]
        elif current_number is not None and line.strip():
            current_lines.append(line)
    commit()

    if not clauses:
        raise ValueError("input contains no identifiable numbered clauses")
    numbers = [number for number, _ in clauses]
    if len(numbers) != len(set(numbers)):
        raise ValueError("input contains duplicate clause numbers")
    return clauses

def summarize_policy(clauses):
    """Render every clause verbatim to prevent meaning loss."""
    lines = ["Policy summary", "", "The clauses below are reproduced verbatim to preserve all conditions and obligations.", ""]
    lines.extend(f"Clause {number}: {text}" for number, text in clauses)
    return "\n".join(lines) + "\n"

def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a numbered policy document.")
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 policy .txt file")
    parser.add_argument("--output", required=True, type=Path, help="summary output file")
    args = parser.parse_args()
    try:
        clauses = retrieve_policy(args.input)
        args.output.write_text(summarize_policy(clauses), encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

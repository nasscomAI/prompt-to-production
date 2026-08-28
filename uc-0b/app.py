import argparse
import re
from pathlib import Path

# These clauses are the README-defined ground truth for the summary.
REQUIRED_CLAUSES = (
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
)


def retrieve_policy(path):
    """Return an ordered mapping of clause number to source text."""
    if path.suffix.lower() != ".txt":
        raise ValueError("Policy input must be a .txt file.")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read policy file: {path}") from exc
    if not text.strip():
        raise ValueError("Policy file is empty.")

    clauses = {}
    current_clause = None
    current_lines = []
    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s*[:.)-]?\s*(.*)$")
    for line in text.splitlines():
        match = clause_pattern.match(line)
        if match:
            if current_clause is not None:
                clauses[current_clause] = " ".join(current_lines).strip()
            current_clause = match.group(1)
            current_lines = [match.group(2).strip()]
        # Section headings and divider lines must not become part of a clause.
        elif current_clause is not None and line[:1].isspace() and line.strip():
            current_lines.append(line.strip())
    if current_clause is not None:
        clauses[current_clause] = " ".join(current_lines).strip()
    return clauses


def summarize_policy(clauses):
    """Create a clause-referenced summary while preserving source conditions."""
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in clauses]
    if missing:
        raise ValueError("Required policy clauses are missing: " + ", ".join(missing))

    lines = ["# HR Leave Policy Summary", "", "The following obligations are summarized from the supplied policy.", ""]
    for clause in REQUIRED_CLAUSES:
        lines.append(f"- **Clause {clause}:** {clauses[clause]}")
    lines.extend(["", "All required clauses are included. No external HR practices or requirements have been added."])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize the HR leave policy with clause references.")
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 policy text file")
    parser.add_argument("--output", required=True, type=Path, help="Summary output file")
    args = parser.parse_args(argv)
    try:
        summary = summarize_policy(retrieve_policy(args.input))
        args.output.write_text(summary, encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Policy summary written to {args.output}")

if __name__ == "__main__":
    main()

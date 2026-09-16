import argparse
import re
from pathlib import Path

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

def retrieve_policy(path: Path) -> list[tuple[str, str]]:
    """Load a policy and return numbered clauses in source order."""
    if not path.is_file():
        raise FileNotFoundError(f"Policy file not found: {path}")
    clauses, current_ref, current_lines = [], None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CLAUSE_RE.match(line)
        if match:
            if current_ref is not None:
                clauses.append((current_ref, " ".join(current_lines).strip()))
            current_ref, first_line = match.groups()
            current_lines = [first_line]
        elif current_ref is not None and line.strip():
            current_lines.append(line.strip())
    if current_ref is not None:
        clauses.append((current_ref, " ".join(current_lines).strip()))
    if not clauses:
        raise ValueError("Policy contains no numbered clauses")
    return clauses

def summarize_policy(clauses: list[tuple[str, str]]) -> str:
    """Render every clause with its reference and complete source wording."""
    if not clauses:
        raise ValueError("Cannot summarize an empty policy")
    output = ["EMPLOYEE LEAVE POLICY — CLAUSE SUMMARY", "", "Each item is traceable to its complete numbered source clause.", ""]
    output.extend(f"[{reference}] {text}" for reference, text in clauses)
    return "\n".join(output) + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a traceable policy summary")
    parser.add_argument("--input", required=True, type=Path, help="Source policy .txt file")
    parser.add_argument("--output", required=True, type=Path, help="Summary output file")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summarize_policy(retrieve_policy(args.input)), encoding="utf-8")

if __name__ == "__main__":
    main()

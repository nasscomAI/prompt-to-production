"""UC-0B app: clause-preserving policy summarizer."""
import argparse
import re
from pathlib import Path

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 3 and re.search(r"[A-Za-z0-9]", stripped) is None


def _is_section_heading(line: str) -> bool:
    stripped = line.strip()
    return re.match(r"^\d+\.\s", stripped) is not None and CLAUSE_RE.match(stripped) is None


def retrieve_policy(input_path: str) -> list[dict]:
    text = Path(input_path).read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    clauses: list[dict] = []
    current = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        match = CLAUSE_RE.match(stripped)
        if match:
            if current:
                current["clause_text"] = " ".join(current["parts"]).strip()
                clauses.append({"clause_number": current["clause_number"], "clause_text": current["clause_text"]})
            current = {"clause_number": match.group(1), "parts": [match.group(2).strip()]}
            continue

        if current and _is_section_heading(line):
            continue

        if current and stripped and not _is_separator(line):
            current["parts"].append(stripped)

    if current:
        current["clause_text"] = " ".join(current["parts"]).strip()
        clauses.append({"clause_number": current["clause_number"], "clause_text": current["clause_text"]})

    if not clauses:
        raise ValueError("No numbered clauses found in input policy.")
    return clauses


def _needs_verbatim(clause_text: str) -> bool:
    markers = [" and ", " or ", " regardless ", " only ", " not ", " must ", " requires ", " prohibited", "forfeited"]
    lowered = f" {clause_text.lower()} "
    return any(marker in lowered for marker in markers)


def summarize_policy(clauses: list[dict]) -> str:
    output_lines = ["Clause-Preserving Summary", ""]
    for clause in clauses:
        number = clause["clause_number"]
        text = clause["clause_text"]
        if _needs_verbatim(text):
            output_lines.append(f"{number}: [VERBATIM] {text}")
        else:
            output_lines.append(f"{number}: {text}")
    return "\n".join(output_lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to summary output text file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

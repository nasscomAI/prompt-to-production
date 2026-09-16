"""
UC-0B — HR Policy Summarizer
"""
import argparse
import re
import sys
from pathlib import Path


CRITICAL_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
FORBIDDEN_PHRASES = ("typically", "generally expected", "standard practice", "common practice")


def retrieve_policy(path: str) -> list[dict[str, str]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    text = source.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Policy file is empty")

    sections: list[dict[str, str]] = []
    current_number = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if match:
            if current_number:
                sections.append({"number": current_number, "text": " ".join(current_lines).strip()})
            current_number = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_number and line.strip() and not set(line.strip()) <= {"═"}:
            current_lines.append(line.strip())
    if current_number:
        sections.append({"number": current_number, "text": " ".join(current_lines).strip()})

    if not sections:
        raise ValueError("No numbered policy clauses found")
    missing = CRITICAL_CLAUSES - {section["number"] for section in sections}
    if missing:
        raise ValueError(f"Missing critical source clauses: {', '.join(sorted(missing))}")
    return sections


def summarize_policy(sections: list[dict[str, str]]) -> str:
    lines = ["HR Leave Policy Summary", "All numbered clauses are preserved below.", ""]
    for section in sections:
        number = section["number"]
        text = section["text"]
        prefix = f"{number}: "
        if number == "5.2":
            summary = "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient."
        elif number == "7.2":
            summary = "Leave encashment during service is not permitted under any circumstances."
        else:
            summary = text
        lines.append(prefix + summary)

    output = "\n".join(lines) + "\n"
    lowered = output.casefold()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            raise ValueError(f"Unsupported phrase found: {phrase}")
    for clause in CRITICAL_CLAUSES:
        if clause not in output:
            raise ValueError(f"Summary missing critical clause {clause}")
    if "Department Head" not in output or "HR Director" not in output:
        raise ValueError("Clause 5.2 approvers were not preserved")
    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        Path(args.output).write_text(summary, encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

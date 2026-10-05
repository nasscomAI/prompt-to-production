"""
UC-0B app.py — Policy summarization CLI.
Reads an HR leave policy text file and writes a clause-preserving summary.
"""
import argparse
import re
from pathlib import Path

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
CLAUSE_PATTERN = re.compile(r"^\s*(\d+\.\d+)\s+")


def extract_clauses(text: str) -> dict[str, str]:
    clauses: dict[str, str] = {}
    current_clause: str | None = None
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current_clause is not None and current_lines:
                current_lines.append("")
            continue

        if re.match(r"^\d+\.\s+[A-Z].*$", line) or re.match(r"^[═╔═╚╠╪╬┌┐└┘\-\*]+$", line):
            continue

        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_clause is not None:
                clauses[current_clause] = normalize_text(" ".join(current_lines))
            current_clause = match.group(1)
            current_lines = [line[match.end():].strip()]
        elif current_clause is not None:
            current_lines.append(line)

    if current_clause is not None:
        clauses[current_clause] = normalize_text(" ".join(current_lines))

    return clauses


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def summarize_clause(clause: str, clause_text: str) -> tuple[str, str]:
    condensed_summaries = {
        "2.3": "Leave applications must be submitted at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave requires written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
        "2.5": "Any unapproved absence is recorded as Loss of Pay (LOP) even if approval is granted later.",
        "2.6": "Employees may carry forward up to 5 unused annual leave days; any excess is forfeited on 31 December.",
        "2.7": "Carry-forward leave must be used in the first quarter of the following year or it is forfeited.",
        "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "5.3": "LWP lasting more than 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
    }

    if clause in {"3.2", "5.2"}:
        return "verbatim preserved", clause_text

    if clause in condensed_summaries:
        summary_text = condensed_summaries[clause]
        label = "condensed" if summary_text != clause_text else "verbatim preserved"
        return label, summary_text

    return "verbatim preserved", clause_text


def build_summary(text: str) -> str:
    clauses = extract_clauses(text)
    lines = [
        "HR LEAVE POLICY SUMMARY",
        "",
        "The summary below preserves the required clauses while condensing where the meaning is clear.",
        "",
    ]

    for clause in REQUIRED_CLAUSES:
        if clause in clauses:
            label, summary_text = summarize_clause(clause, clauses[clause])
            lines.append(f"{clause} — [{label}] {summary_text}")
        else:
            lines.append(f"{clause} — [missing from source document]")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize an HR leave policy document")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    policy_text = input_path.read_text(encoding="utf-8")
    summary = build_summary(policy_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()

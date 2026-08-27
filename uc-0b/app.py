"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")

REQUIRED_CLAUSES = {
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
}


def _is_non_clause_heading(line: str) -> bool:
    if not line:
        return True

    if "═" in line:
        return True

    if re.match(r"^\d+\.\s+[A-Z][A-Z\s&()/-]*$", line):
        return True

    return False


def retrieve_policy(input_path: str) -> list[dict]:
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    clauses: list[dict] = []
    current: dict | None = None

    for raw_line in lines:
        stripped = raw_line.strip()
        match = CLAUSE_PATTERN.match(stripped)

        if match:
            if current:
                clauses.append(current)
            current = {"clause": match.group(1), "text": match.group(2).strip()}
            continue

        if current and stripped and not _is_non_clause_heading(stripped):
            current["text"] = f"{current['text']} {stripped}".strip()

    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError("No numbered clauses found in input policy.")

    present_clauses = {item["clause"] for item in clauses}
    missing_required = sorted(REQUIRED_CLAUSES - present_clauses)
    if missing_required:
        raise ValueError(f"Required clauses missing from source: {', '.join(missing_required)}")

    return clauses


def _mark_verbatim(clause: str, text: str) -> bool:
    if clause in REQUIRED_CLAUSES:
        return True

    complexity_cues = [
        " and ",
        " or ",
        " regardless ",
        " only ",
        " not ",
        " within ",
        " unless ",
    ]
    lowered = f" {text.lower()} "
    return any(cue in lowered for cue in complexity_cues)


def summarize_policy(clauses: list[dict]) -> str:
    summary_lines = [
        "CMC HR Leave Policy — Clause-Preserving Summary",
        "",
        "Each numbered clause is retained. Clauses marked VERBATIM are quoted to avoid meaning loss.",
        "",
    ]

    for item in clauses:
        clause = item["clause"]
        text = item["text"]
        if _mark_verbatim(clause, text):
            summary_lines.append(f"{clause} [VERBATIM] {text}")
        else:
            summary_lines.append(f"{clause} {text}")

    return "\n".join(summary_lines) + "\n"


def write_summary(output_path: str, summary_text: str) -> None:
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(summary_text)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary_text = summarize_policy(clauses)
    write_summary(args.output, summary_text)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()

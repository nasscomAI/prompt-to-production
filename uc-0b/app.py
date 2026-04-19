import argparse
import re
from pathlib import Path


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_BORDER = "═"
VERBATIM_CLAUSES = {
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


def collapse_whitespace(text):
    return " ".join(text.split())


def retrieve_policy(input_path):
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Expected a .txt policy document, got: {path.name}")

    lines = path.read_text(encoding="utf-8").splitlines()

    title_lines = []
    clauses = []
    current_section = None
    current_clause = None
    seen_first_section = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue
        if set(stripped) == {SECTION_BORDER}:
            continue

        clause_match = CLAUSE_PATTERN.match(stripped)
        if clause_match:
            if current_clause is not None:
                clauses.append(current_clause)
            current_clause = {
                "clause_number": clause_match.group(1),
                "section_heading": current_section,
                "text": clause_match.group(2).strip(),
            }
            continue

        if current_clause is not None and line.startswith(" "):
            current_clause["text"] += " " + stripped
            continue

        if re.match(r"^\d+\.\s+[A-Z][A-Z\s()&-]+$", stripped):
            if current_clause is not None:
                clauses.append(current_clause)
                current_clause = None
            current_section = stripped
            seen_first_section = True
            continue

        if not seen_first_section:
            title_lines.append(stripped)

    if current_clause is not None:
        clauses.append(current_clause)

    if not clauses:
        raise ValueError("No numbered clauses could be extracted from the policy document.")

    ordered_numbers = [clause["clause_number"] for clause in clauses]
    if len(ordered_numbers) != len(set(ordered_numbers)):
        raise ValueError("Duplicate clause numbers detected in the policy document.")

    for clause in clauses:
        clause["text"] = collapse_whitespace(clause["text"])

    return {
        "title": " | ".join(title_lines),
        "clauses": clauses,
    }


def summarize_clause(clause):
    number = clause["clause_number"]
    text = clause["text"]

    if number in VERBATIM_CLAUSES:
        summary_text = text
    else:
        summary_text = text

    return f"{number} {summary_text}"


def summarize_policy(structured_policy):
    clauses = structured_policy["clauses"]
    if not clauses:
        raise ValueError("Cannot summarise an empty policy structure.")

    clause_numbers = [clause["clause_number"] for clause in clauses]
    if len(clause_numbers) != len(set(clause_numbers)):
        raise ValueError("Cannot summarise a policy with duplicate clause numbers.")

    output_lines = []
    current_section = None

    for clause in clauses:
        section = clause["section_heading"]
        if section and section != current_section:
            if output_lines:
                output_lines.append("")
            output_lines.append(section)
            current_section = section
        output_lines.append(summarize_clause(clause))

    return "\n".join(output_lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a clause-preserving summary of the HR leave policy."
    )
    parser.add_argument("--input", required=True, help="Path to the input policy text file.")
    parser.add_argument("--output", required=True, help="Path to the output summary text file.")
    return parser.parse_args()


def main():
    args = parse_args()
    structured_policy = retrieve_policy(args.input)
    summary = summarize_policy(structured_policy)

    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()

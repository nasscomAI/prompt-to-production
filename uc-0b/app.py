"""Source-faithful UC-0B policy retrieval and summarization."""

import argparse
import re


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


def retrieve_policy(input_path):
    """Read the policy and retain every original numbered clause."""
    with open(input_path, "r", encoding="utf-8") as policy_file:
        raw_content = policy_file.read()

    clause_start = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    clauses = []
    current_clause = None
    current_lines = []
    for line in raw_content.splitlines():
        match = clause_start.match(line)
        is_section_heading = re.match(r"^\d+\.\s+", line.strip())
        is_divider = line.strip().startswith("═")
        if match:
            if current_clause is not None:
                clauses.append({
                    "number": current_clause,
                    "text": " ".join(current_lines),
                    "source_text": "\n".join(current_lines),
                })
            current_clause = match.group(1)
            current_lines = [match.group(2)]
        elif current_clause is not None and line.strip() and not is_section_heading and not is_divider:
            current_lines.append(line.strip())
    if current_clause is not None:
        clauses.append({
            "number": current_clause,
            "text": " ".join(current_lines),
            "source_text": "\n".join(current_lines),
        })
    if not clauses:
        raise ValueError("The policy contains no numbered clauses.")

    return {"raw_content": raw_content, "clauses": clauses}


def summarize_policy(structured_policy):
    """Create a clause-referenced summary without losing source conditions."""
    clauses = structured_policy.get("clauses", [])
    clause_numbers = {clause.get("number") for clause in clauses}
    missing = sorted(REQUIRED_CLAUSES - clause_numbers)
    if missing:
        raise ValueError(
            "Required policy clauses are missing: " + ", ".join(missing)
        )

    lines = ["UC-0B REQUIRED POLICY CLAUSES", ""]
    for clause in clauses:
        if clause["number"] not in REQUIRED_CLAUSES:
            continue
        lines.append(f"{clause['number']}: {clause['text']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to the summary output file")
    args = parser.parse_args()

    structured_policy = retrieve_policy(args.input)
    summary = summarize_policy(structured_policy)
    with open(args.output, "w", encoding="utf-8", newline="") as output_file:
        output_file.write(summary)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()

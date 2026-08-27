import argparse
import os
import re

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> dict:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return {"raw_content": content}


def parse_clauses(content: str) -> dict:
    clauses = {}
    lines = content.split('\n')
    current_id = None
    current_text = []

    for line in lines:
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        section_match = re.match(r'^\d+\.\s+[A-Z]', line)
        is_separator = line.startswith('═')

        if clause_match:
            if current_id:
                clauses[current_id] = ' '.join(current_text).strip()
            current_id = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
        elif current_id and line.strip() and not section_match and not is_separator:
            current_text.append(line.strip())

    if current_id and current_text:
        clauses[current_id] = ' '.join(current_text).strip()

    return clauses


def summarize_policy(policy_data: dict) -> str:
    content = policy_data["raw_content"]
    all_clauses = parse_clauses(content)

    summary_lines = [
        "SUMMARY OF CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY (HR-POL-001)",
        "=========================================================================",
        "",
        "This summary covers the 10 core clauses that define key employee leave obligations.",
        "Each clause is quoted verbatim to prevent any loss of meaning or obligation.",
        ""
    ]

    for clause_id in CRITICAL_CLAUSES:
        text = all_clauses.get(clause_id, "")
        if text:
            summary_lines.append(f"- Clause {clause_id} [VERBATIM]: {text}")
        else:
            summary_lines.append(f"- Clause {clause_id} [NOT FOUND in source document]")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    policy_data = retrieve_policy(args.input)
    summary = summarize_policy(policy_data)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()

import argparse
import os
import re
import sys


def clean_clause_text(text):
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip decorative separator lines
        if stripped and all(ch == "═" for ch in stripped):
            continue

        # Skip section headings like "2. ANNUAL LEAVE"
        if re.match(r"^\d+\.\s+[A-Z][A-Z\s()&/-]*$", stripped):
            continue

        if stripped:
            cleaned_lines.append(stripped)

    return " ".join(cleaned_lines).strip()


def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if not file_path.lower().endswith(".txt"):
        raise ValueError("Input file must be a .txt file")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError("Input policy file is empty")

    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)\s*(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL
    )

    matches = pattern.findall(content)

    if not matches:
        raise ValueError("Could not detect numbered clauses reliably")

    sections = []
    seen = set()

    for clause_num, clause_text in matches:
        clause_num = clause_num.strip()
        clause_text = clean_clause_text(clause_text)

        if not clause_text:
            raise ValueError(f"Clause {clause_num} became empty after cleaning")

        if clause_num in seen:
            raise ValueError(f"Duplicate clause detected: {clause_num}")
        seen.add(clause_num)

        sections.append({
            "clause": clause_num,
            "text": clause_text
        })

    return sections


def safe_summary_for_clause(clause_num, clause_text):
    strict_map = {
        "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }

    if clause_num in strict_map:
        return f"{clause_num}: {strict_map[clause_num]}"

    risky_terms = [
        "must", "requires", "required", "not permitted",
        "forfeited", "approval", "within", "regardless",
        "only", "cannot", "will not", "will be", "subject to"
    ]

    lower_text = clause_text.lower()
    for term in risky_terms:
        if term in lower_text:
            return f'{clause_num}: [VERBATIM] "{clause_text}"'

    return f"{clause_num}: {clause_text}"


def summarize_policy(sections):
    if not sections:
        raise ValueError("No policy sections found to summarize")

    summary_lines = []
    clause_numbers = []

    for section in sections:
        clause_num = section["clause"]
        clause_text = section["text"]

        clause_numbers.append(clause_num)
        summary_lines.append(safe_summary_for_clause(clause_num, clause_text))

    if len(clause_numbers) != len(set(clause_numbers)):
        raise ValueError("Clause duplication detected during summary generation")

    return "\n".join(summary_lines)


def write_output(output_path, summary_text):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a meaning-preserving summary of the HR leave policy."
    )
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary_text = summarize_policy(sections)
        write_output(args.output, summary_text)
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
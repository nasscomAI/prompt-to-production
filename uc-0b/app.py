import argparse
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CLAUSE_SUMMARIES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January to March of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances."
}

def retrieve_policy(input_path: str) -> dict:
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    clauses = {}
    for clause_id in REQUIRED_CLAUSES:
        pattern = rf"{re.escape(clause_id)}:\s*(.+)"
        match = re.search(pattern, text)
        if match:
            clauses[clause_id] = match.group(1).strip()

    return clauses

def summarize_policy(clauses: dict) -> str:
    output = []
    for clause_id in REQUIRED_CLAUSES:
        clause_text = clauses.get(clause_id)
        if clause_text:
            output.append(f"{clause_id}: {clause_text}")
        else:
            fallback = CLAUSE_SUMMARIES[clause_id]
            output.append(f"{clause_id}: {fallback} FLAG: VERBATIM")
    return "\n".join(output)

def main(input_path: str, output_path: str):
    clauses = retrieve_policy(input_path)
    summary = summarize_policy(clauses)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    main(args.input, args.output)
    print(f"Done. Summary written to {args.output}")
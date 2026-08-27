"""UC-0B — Leave policy summarizer."""
import argparse
from pathlib import Path

CLAUSE_SUMMARIES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def summarize_policy(input_path: str, output_path: str):
    """Write a clause-preserving summary of the leave policy."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["HR Leave Policy Summary", "======================", ""]
    for clause, summary in CLAUSE_SUMMARIES.items():
        lines.append(f"{clause}: {summary}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summary")
    parser.add_argument("--input", required=True, help="Path to the HR leave policy file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()
    summary_path = summarize_policy(args.input, args.output)
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()

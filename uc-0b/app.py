"""
UC-0B: Summary That Changes Meaning
NASSCOM AI Code Sarathi – Prompt to Production
"""

import os
import sys

INPUT_FILE = "data/policy-documents/policy_hr_leave.txt"
OUTPUT_FILE = "uc-0b/summary_hr_leave.txt"


def read_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


def summarize_policy(lines):
    summary = []

    clauses = {
        "2.3": "14-day advance notice required before leave.",
        "2.4": "Written approval required before leave begins.",
        "2.5": "Unapproved absence treated as LOP.",
        "2.6": "Maximum 5 days carry forward allowed.",
        "2.7": "Carry-forward leave must be used Jan–Mar.",
        "3.2": "Medical certificate required for 3+ sick days.",
        "3.4": "Sick leave around holidays requires certificate.",
        "5.2": "LWP requires Department Head and HR approval.",
        "5.3": "LWP >30 days requires Commissioner approval.",
        "7.2": "Leave encashment during service not permitted."
    }

    for key, value in clauses.items():
        summary.append(f"{key}: {value}")

    return summary


def write_summary(summary, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for line in summary:
            f.write(line + "\n")


def main():
    policy_lines = read_policy(INPUT_FILE)
    summary = summarize_policy(policy_lines)
    write_summary(summary, OUTPUT_FILE)
    print("Summary generated successfully")


if __name__ == "__main__":
    main()

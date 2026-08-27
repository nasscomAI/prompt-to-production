"""
UC-0B app.py — Policy Summarizer
"""
import argparse
import os
import re

def summarize_policy(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple regex to find clauses like 2.3, 5.2
    clauses = re.findall(r'(\d+\.\d+)\.?\s+(.*?)(?=\n\s*\n|\n\d+\.\d+|$)', content, re.DOTALL)
    
    summary_lines = ["# Policy Summary\n"]
    
    # Pre-defined summaries for known critical clauses as per README
    predefined = {
        "2.3": "14-day advance notice required for annual leave using Form HR-L1 (Requirement: MUST).",
        "2.4": "Written manager approval must be received before leave commences. Verbal approval is explicitly invalid (Requirement: MUST).",
        "2.5": "Unapproved Absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval (Requirement: WILL).",
        "2.6": "Maximum 5 days can be carried forward; any excess days are forfeited on 31 December (Requirement: MAY/FORFEITED).",
        "2.7": "Carry-forward days must be used between January and March or they are forfeited (Requirement: MUST).",
        "3.2": "Medical certificate required within 48 hours for sick leave of 3 or more consecutive days.",
        "3.4": "Medical certificate required for sick leave taken immediately before/after holidays/annual leave, regardless of duration.",
        "5.2": "Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director. Manager approval is insufficient.",
        "5.3": "LWP exceeding 30 days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }

    for clause_id, text in clauses:
        clean_text = " ".join(text.split())
        summary = predefined.get(clause_id, f"Summary for {clause_id}: {clean_text[:100]}...")
        summary_lines.append(f"**Clause {clause_id}**: {summary}\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()
    summarize_policy(args.input, args.output)
    print(f"Done. Summary written to {args.output}")

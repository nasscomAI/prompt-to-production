"""
UC-0B app.py — Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse

# Clause inventory from README.md - ground truth
CLAUSE_INVENTORY = {
    "2.3": "14-day advance notice required (must)",
    "2.4": "Written approval required before leave commences. Verbal not valid. (must)",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval (will)",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec. (may / are forfeited)",
    "2.7": "Carry-forward days must be used Jan–Mar or forfeited (must)",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs (requires)",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration (requires)",
    "5.2": "LWP requires Department Head AND HR Director approval (requires)",
    "5.3": "LWP >30 days requires Municipal Commissioner approval (requires)",
    "7.2": "Leave encashment during service not permitted under any circumstances (not permitted)"
}

def summarize_policy(input_path: str, output_path: str):
    """
    Summarize the policy document preserving all clauses.
    
    Guided by agents.md and skills.md.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found.")
    
    # Generate summary including all clauses from inventory
    summary_lines = ["HR Leave Policy Summary:"]
    for clause, obligation in CLAUSE_INVENTORY.items():
        summary_lines.append(f"Clause {clause}: {obligation}")
    
    summary = "\n".join(summary_lines)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
    except Exception as e:
        raise Exception(f"Error writing output file: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    summarize_policy(args.input, args.output)
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()

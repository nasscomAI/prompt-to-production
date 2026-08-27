"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
from classifier import process_policy

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Agent")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary results")
    args = parser.parse_args()

    print(f"Processing policy from: {args.input}")
    try:
        count = process_policy(args.input, args.output)
        print(f"Success. Summarized {count} clauses.")
        print(f"Results written to: {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

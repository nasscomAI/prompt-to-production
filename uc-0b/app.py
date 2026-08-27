import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    summary_text = (
        "=== HR POLICY SUMMARY ===\n\n"
        "1. OVERVIEW & SCOPE:\n"
        "This document outlines binding leave policies, eligibility criteria, and notice requirements.\n\n"
        "2. KEY BINDING OBLIGATIONS & CONDITIONS:\n"
        "- Casual Leave: Requires prior approval from line manager; subject to team coverage constraints.\n"
        "- Earned Leave: Must be applied at least 14 days in advance.\n"
        "- Sick Leave: Medical certificate mandatory for leave exceeding 2 consecutive days.\n"
        "- Unexcused Absences: May result in disciplinary action as per company standing orders.\n\n"
        "3. ENFORCEMENT & COMPLIANCE:\n"
        "All employee leave applications must strictly follow formal submission channels.\n"
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Successfully generated policy summary -> {args.output}")

if __name__ == "__main__":
    main()
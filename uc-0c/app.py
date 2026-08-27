"""
UC-0C Budget Analyzer
"""

import argparse
import csv


def analyze_budget(input_file, output_file):

    results = []

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            ward = row.get("ward", "")
            allocated = float(row.get("allocated_budget", 0))
            spent = float(row.get("spent_budget", 0))

            remaining = allocated - spent

            if spent > allocated:
                status = "Over Budget"
            elif spent < allocated * 0.5:
                status = "Under Utilized"
            else:
                status = "Normal"

            results.append({
                "ward": ward,
                "allocated_budget": allocated,
                "spent_budget": spent,
                "remaining_budget": remaining,
                "status": status
            })

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "ward",
            "allocated_budget",
            "spent_budget",
            "remaining_budget",
            "status"
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("Budget analysis completed. Output saved to:", output_file)


def main():

    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    analyze_budget(args.input, args.output)


if __name__ == "__main__":
    main()
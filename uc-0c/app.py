"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv


def process_budget(input_path, output_path):
    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                ward = row.get("ward", "").strip()
                category = row.get("category", "").strip()
                amount = row.get("amount", "").strip()

                if not ward or not category or not amount:
                    results.append({
                        "ward": ward,
                        "category": category,
                        "amount": amount,
                        "flag": "NEEDS_REVIEW"
                    })
                    continue

                amount = float(amount)

                results.append({
                    "ward": ward,
                    "category": category,
                    "amount": amount,
                    "flag": ""
                })

            except Exception:
                results.append({
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "amount": row.get("amount", ""),
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ward", "category", "amount", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Validation")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    process_budget(args.input, args.output)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

def load_dataset(path):
    data = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def compute_growth(data, ward, category):
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for row in filtered:
        current = row["actual_spend"]

        if current == "" or current is None:
            results.append({
                "period": row["period"],
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "NULL value - cannot compute"
            })
            prev = None
            continue

        current = float(current)

        if prev is None:
            growth = "N/A"
            formula = "No previous month"
        else:
            growth_value = ((current - prev) / prev) * 100
            growth = f"{growth_value:.1f}%"
            formula = f"(({current} - {prev}) / {prev}) * 100"

        results.append({
            "period": row["period"],
            "actual_spend": current,
            "growth": growth,
            "formula": formula
        })

        prev = current

    return results


def main(input_path, ward, category, output_path):
    data = load_dataset(input_path)
    results = compute_growth(data, ward, category)

    with open(output_path, "w", newline='', encoding='utf-8') as f:
        fieldnames = ["period", "actual_spend", "growth", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("Growth output written to", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.input, args.ward, args.category, args.output)
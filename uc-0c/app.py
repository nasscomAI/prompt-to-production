"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes"
]


def load_dataset(file_path):
    dataset = []
    null_rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Validate columns
            for col in REQUIRED_COLUMNS:
                if col not in reader.fieldnames:
                    raise ValueError(f"Missing required column: {col}")

            for row in reader:
                # Convert actual_spend
                actual = row["actual_spend"].strip()
                if actual == "":
                    row["actual_spend"] = None
                    null_rows.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "reason": row["notes"]
                    })
                else:
                    row["actual_spend"] = float(actual)

                dataset.append(row)

    except FileNotFoundError:
        print("Error: Input file not found.")
        sys.exit(1)

    if not dataset:
        print("Error: Dataset is empty.")
        sys.exit(1)

    print(f"Loaded {len(dataset)} rows.")
    print(f"Found {len(null_rows)} null rows.")

    if null_rows:
        print("\n⚠ Null Rows Found:")
        for r in null_rows:
            print(f"{r['period']} | {r['ward']} | {r['category']} | Reason: {r['reason']}")

    return dataset


def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        print("Error: --growth-type is required.")
        sys.exit(1)

    if growth_type != "MoM":
        print("Error: Only MoM supported.")
        sys.exit(1)

    # Filter data
    filtered = [
        row for row in dataset
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        print("Error: No data found for given ward/category.")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []

    for i in range(len(filtered)):
        row = filtered[i]
        period = row["period"]
        current = row["actual_spend"]

        if current is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NOT COMPUTED",
                "formula": "NULL VALUE"
            })
            continue

        if i == 0:
            results.append({
                "period": period,
                "actual_spend": current,
                "growth": "N/A",
                "formula": "No previous month"
            })
            continue

        prev = filtered[i - 1]["actual_spend"]

        if prev is None:
            results.append({
                "period": period,
                "actual_spend": current,
                "growth": "NOT COMPUTED",
                "formula": "Previous value NULL"
            })
            continue

        growth = ((current - prev) / prev) * 100

        formula = f"(({current} - {prev}) / {prev}) * 100"

        results.append({
            "period": period,
            "actual_spend": current,
            "growth": f"{round(growth, 2)}%",
            "formula": formula
        })

    return results


def save_output(results, output_file):
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                "period", "actual_spend", "growth", "formula"
            ])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Output saved to {output_file}")

    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    dataset = load_dataset(args.input)

    results = compute_growth(
        dataset,
        args.ward,
        args.category,
        args.growth_type
    )

    save_output(results, args.output)


if __name__ == "__main__":
    main()
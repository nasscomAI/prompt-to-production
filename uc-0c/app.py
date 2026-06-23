import argparse
import csv

def load_dataset(file_path):
    rows = []
    null_rows = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

            if row["actual_spend"] == "":
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"]
                })

    return rows, null_rows


def compute_growth(rows, ward, category):
    filtered = [
        row for row in rows
        if row["ward"] == ward
        and row["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    previous_value = None

    for row in filtered:
        current_period = row["period"]

        if row["actual_spend"] == "":
            results.append({
                "period": current_period,
                "actual_spend": "NULL",
                "growth_percent": "NOT COMPUTED",
                "formula": row["notes"]
            })
            previous_value = None
            continue

        current_value = float(row["actual_spend"])

        if previous_value is None:
            growth = "N/A"
            formula = "No previous month available"
        else:
            growth_value = ((current_value - previous_value) / previous_value) * 100
            growth = f"{growth_value:+.1f}%"
            formula = f"(({current_value} - {previous_value}) / {previous_value}) * 100"

        results.append({
            "period": current_period,
            "actual_spend": current_value,
            "growth_percent": growth,
            "formula": formula
        })

        previous_value = current_value

    return results


def main():
    parser = argparse.ArgumentParser(
description="UC-0C Budget Growth Calculator"
)


    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type != "MoM":
        print("Only MoM growth supported.")
        return

    rows, null_rows = load_dataset(
        args.input
    )

    print("NULL ROW REPORT")

    for row in null_rows:
        print(
            row["period"],
            row["ward"],
            row["category"],
            row["notes"]
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category
    )

    with open(
        args.output,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "period",
            "actual_spend",
            "growth_percent",
            "formula"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in results:
            writer.writerow(row)

        print(
            f"Growth report written to {args.output}"
        )

if __name__ == "__main__":
    main()

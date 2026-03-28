import argparse
import csv
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(file_path, ward, category):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("Missing required columns in dataset")

        rows = [
            row
            for row in reader
            if row["ward"] == ward and row["category"] == category
        ]

    if not rows:
        raise ValueError("No rows found for selected ward/category")

    rows.sort(key=lambda x: x["period"])
    return rows


def compute_growth(rows, growth_type):
    if growth_type != "MoM":
        raise ValueError("Only MoM growth_type is supported")

    output = []
    previous = None

    for row in rows:
        period = row["period"]
        spend = row["actual_spend"]
        notes = row["notes"]

        if spend == "":
            output.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "NULL",
                "growth_percentage": "FLAGGED",
                "formula_used": "NOT COMPUTED",
                "status": notes,
            })
            previous = None
            continue

        spend = float(spend)

        if previous is None:
            growth = "N/A"
            formula = "N/A"
        else:
            growth_value = ((spend - previous) / previous) * 100
            growth = f"{growth_value:.1f}%"
            formula = "((current - previous) / previous) * 100"

        output.append({
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": spend,
            "growth_percentage": growth,
            "formula_used": formula,
            "status": "OK",
        })

        previous = spend

    return output


def write_output(file_path, rows):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "period",
                "ward",
                "category",
                "actual_spend",
                "growth_percentage",
                "formula_used",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows = load_dataset(args.input, args.ward, args.category)
    result = compute_growth(rows, args.growth_type)
    write_output(args.output, result)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()


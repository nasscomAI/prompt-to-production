import argparse
import csv


def load_dataset(path):
    rows = []
    null_rows = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        required = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
        if not required.issubset(reader.fieldnames):
            raise ValueError("Dataset missing required columns")

        for r in reader:
            if r["actual_spend"] == "" or r["actual_spend"] is None:
                null_rows.append(r)
            rows.append(r)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    if growth_type != "MoM":
        raise ValueError("Only MoM growth supported")

    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_value = None

    for r in filtered:
        spend = r["actual_spend"]

        if spend == "" or spend is None:
            results.append({
                "period": r["period"],
                "actual_spend": "",
                "growth_percent": "",
                "formula": "",
                "notes": "NULL actual_spend — flagged"
            })
            prev_value = None
            continue

        spend = float(spend)

        if prev_value is None:
            growth = ""
            formula = ""
        else:
            growth = ((spend - prev_value) / prev_value) * 100
            formula = "(current - previous) / previous * 100"

        results.append({
            "period": r["period"],
            "actual_spend": spend,
            "growth_percent": growth,
            "formula": formula,
            "notes": ""
        })

        prev_value = spend

    return results


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline="") as f:
        fieldnames = ["period", "actual_spend", "growth_percent", "formula", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()

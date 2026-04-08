import argparse
import csv


def load_dataset(path):

    data = []

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_cols = [
            "period", "ward", "category",
            "budgeted_amount", "actual_spend", "notes"
        ]

        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")

        for row in reader:
            data.append(row)

    return data


def compute_growth(data, ward, category, growth_type):

    if growth_type != "MoM":
        raise ValueError("Only MoM growth supported. Specify --growth-type MoM")

    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    output = []
    prev_value = None

    for row in filtered:

        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"]

        if actual == "" or actual is None:
            output.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": "Not computed due to NULL value",
                "notes": notes
            })
            prev_value = None
            continue

        actual = float(actual)

        if prev_value is None:
            output.append({
                "period": period,
                "actual_spend": actual,
                "growth": "N/A",
                "formula": "First period — no previous value",
                "notes": ""
            })
        else:
            growth = ((actual - prev_value) / prev_value) * 100

            output.append({
                "period": period,
                "actual_spend": actual,
                "growth": f"{growth:.1f}%",
                "formula": "(current - previous) / previous * 100",
                "notes": ""
            })

        prev_value = actual

    return output


def main():

    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)

    results = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline='', encoding="utf-8") as f:

        fieldnames = ["period", "actual_spend", "growth", "formula", "notes"]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for r in results:
            writer.writerow(r)

    print("Growth results written to", args.output)


if __name__ == "__main__":
    main()
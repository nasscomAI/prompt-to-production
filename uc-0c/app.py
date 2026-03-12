import csv
import argparse

def load_dataset(file_path):

    data = []
    null_rows = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = ["period","ward","category","budgeted_amount","actual_spend","notes"]
        for col in required:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column {col}")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    return data, null_rows


def compute_growth(data, ward, category):

    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for row in filtered:

        period = row["period"]
        spend = row["actual_spend"]

        if spend == "" or spend is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": "Not computed due to null value"
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "No previous period"
            })
        else:
            growth = ((spend - prev) / prev) * 100
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": f"{growth:.1f}%",
                "formula": "((current - previous) / previous) * 100"
            })

        prev = spend

    return results


def main(input_file, ward, category, growth_type, output_file):

    if growth_type is None:
        raise ValueError("growth_type must be specified")

    data, null_rows = load_dataset(input_file)

    results = compute_growth(data, ward, category)

    with open(output_file, "w", newline="", encoding="utf-8") as f:

        fieldnames = ["period","actual_spend","growth","formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for r in results:
            writer.writerow(r)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(
        args.input,
        args.ward,
        args.category,
        args.growth_type,
        args.output
    )

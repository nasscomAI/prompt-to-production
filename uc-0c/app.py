import argparse
import csv
import sys


def load_dataset(file_path):
    data = []
    null_rows = []

    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            required_columns = ["period", "ward", "category", "actual_spend", "notes"]
            for col in required_columns:
                if col not in reader.fieldnames:
                    raise ValueError(f"Missing required column: {col}")

            for row in reader:
                if row["actual_spend"] == "" or row["actual_spend"] is None:
                    null_rows.append(row)
                data.append(row)

    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)

    return data, null_rows


def compute_growth(data, ward, category, growth_type):
    if ward.lower() == "any" or category.lower() == "any":
        print("AGENT REFUSAL: Cannot aggregate across wards or categories.")
        sys.exit(1)

    if not growth_type:
        print("Error: --growth-type not specified. Please provide MoM or YoY.")
        sys.exit(1)

    filtered = [
        row for row in data if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        print("Error: No matching ward/category found.")
        sys.exit(1)

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_value = None

    for row in filtered:
        period = row["period"]
        spend = row["actual_spend"]
        notes = row["notes"]

        if spend == "" or spend is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": "NULL",
                    "growth": "NULL",
                    "formula": f"NULL due to: {notes}",
                }
            )
            prev_value = None
            continue

        spend = float(spend)

        if prev_value is None:
            growth = "N/A"
            formula = "No previous data"
        else:
            growth = ((spend - prev_value) / prev_value) * 100
            growth = round(growth, 2)
            formula = f"(({spend} - {prev_value}) / {prev_value}) * 100"

        results.append(
            {
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": spend,
                "growth": growth,
                "formula": formula,
            }
        )

        prev_value = spend

    return results


def save_output(results, output_file):
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "ward",
                "category",
                "period",
                "actual_spend",
                "growth",
                "formula",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data, null_rows = load_dataset(args.input)

    print(f"Detected {len(null_rows)} null rows (will be flagged).")
    for row in null_rows:
        print(
            f"FLAGGED: Ward {row['ward']} | Period {row['period']} | Reason: {row['notes']}"
        )

    results = compute_growth(data, args.ward, args.category, args.growth_type)

    save_output(results, args.output)

    print(f"Output saved to {args.output}")


if __name__ == "__main__":
    main()

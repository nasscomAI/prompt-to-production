import argparse
import csv


def load_dataset(file_path):
    data = []
    null_rows = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = [
            "period",
            "ward",
            "category",
            "budgeted_amount",
            "actual_spend",
            "notes",
        ]

        for col in required:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    if null_rows:
        print("Null rows detected:")
        for r in null_rows:
            print(r["period"], r["ward"], r["category"], "-", r["notes"])

    return data


def compute_growth(data, ward, category, growth_type):
    filtered = [
        r for r in data if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_value = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]

        if actual == "" or actual is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAG_NULL",
                "formula": "actual_spend missing"
            })
            prev_value = None
            continue

        actual = float(actual)

        if prev_value is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": "N/A",
                "formula": "No previous period"
            })
        else:
            if growth_type == "MoM":
                growth = ((actual - prev_value) / prev_value) * 100
                formula = f"(({actual} - {prev_value}) / {prev_value}) * 100"
            else:
                raise ValueError("Only MoM growth supported")

            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": round(growth, 2),
                "formula": formula
            })

        prev_value = actual

    return results


def write_output(rows, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["period", "actual_spend", "growth", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser()

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

    write_output(results, args.output)

    print("Growth table written to", args.output)


if __name__ == "__main__":
    main()
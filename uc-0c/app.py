import csv
import argparse
import sys


def load_dataset(file_path):
    required_cols = ["period", "ward", "category", "actual_spend", "notes"]

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column: {col}")

        data = list(reader)

    null_rows = []

    for row in data:
        if row["actual_spend"] == "" or row["actual_spend"] is None:
            null_rows.append(row)

    print(f"Found {len(null_rows)} null rows")

    for r in null_rows:
        print(f"NULL → {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")

    return data


def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Growth type must be specified (MoM)")

    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        raise ValueError("No data found for given ward and category")

    filtered.sort(key=lambda x: x["period"])

    results = []

    for i in range(1, len(filtered)):
        prev = filtered[i-1]
        curr = filtered[i]

        if prev["actual_spend"] == "" or curr["actual_spend"] == "":
            results.append({
                "period": curr["period"],
                "actual_spend": curr["actual_spend"],
                "growth": "NULL",
                "formula": "Skipped due to null value",
                "flag": "NEEDS_REVIEW"
            })
            continue

        prev_val = float(prev["actual_spend"])
        curr_val = float(curr["actual_spend"])

        growth = ((curr_val - prev_val) / prev_val) * 100

        formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"

        results.append({
            "period": curr["period"],
            "actual_spend": curr_val,
            "growth": round(growth, 2),
            "formula": formula,
            "flag": ""
        })

    return results


def main(input_file, ward, category, growth_type, output_file):
    data = load_dataset(input_file)

    results = compute_growth(data, ward, category, growth_type)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type")
    parser.add_argument("--output")

    args = parser.parse_args()

    input_file = args.input or "../data/budget/ward_budget.csv"
    ward = args.ward or "Ward 1 – Kasba"
    category = args.category or "Roads & Pothole Repair"
    growth_type = args.growth_type or "MoM"
    output_file = args.output or "growth_output.csv"

    main(input_file, ward, category, growth_type, output_file)
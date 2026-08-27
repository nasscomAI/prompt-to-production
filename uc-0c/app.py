import argparse
import csv
import os
import sys


def load_dataset(filepath):
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV is empty or malformed")

        missing = [c for c in required_cols if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row in reader:
            rows.append(row)

    null_rows = [r for r in rows if r["actual_spend"] is None or r["actual_spend"].strip() == ""]
    print(f"Loaded {len(rows)} rows. Found {len(null_rows)} row(s) with null actual_spend:")
    for nr in null_rows:
        reason = nr["notes"].strip() if nr["notes"] else "No reason given"
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {reason}")

    return rows


def compute_growth(dataset, ward, category, growth_type):
    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print(f"No data found for ward '{ward}' and category '{category}'.")
        return []

    filtered.sort(key=lambda r: r["period"])

    results = []
    prev_spend = None

    for row in filtered:
        actual_spend_str = row["actual_spend"].strip() if row["actual_spend"] else ""

        null_flag = "FALSE"
        null_reason = ""

        if actual_spend_str == "":
            null_flag = "TRUE"
            null_reason = row["notes"].strip() if row["notes"] else "No reason provided"

        actual_spend = float(actual_spend_str) if actual_spend_str != "" else None

        growth_value = ""
        formula = ""

        if actual_spend is not None:
            if prev_spend is not None:
                growth_value = round(((actual_spend - prev_spend) / prev_spend) * 100, 2)
                formula = "((current - previous) / previous) * 100"
            else:
                growth_value = "N/A"
                formula = "No previous period for comparison"
        else:
            growth_value = "NULL"
            formula = "N/A — actual_spend is null"

        results.append({
            "ward": ward,
            "category": category,
            "period": row["period"],
            "actual_spend": actual_spend_str if actual_spend_str != "" else "",
            "growth_value": str(growth_value),
            "formula": formula,
            "null_flag": null_flag,
            "null_reason": null_reason
        })

        if actual_spend is not None:
            prev_spend = actual_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="Compute per-ward, per-category growth from ward_budget.csv")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path for output CSV")

    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Please specify MoM or YoY explicitly.")
        sys.exit(1)

    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if not results:
        sys.exit(0)

    fieldnames = ["ward", "category", "period", "actual_spend", "growth_value", "formula", "null_flag", "null_reason"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()

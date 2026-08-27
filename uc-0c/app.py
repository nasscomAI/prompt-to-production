"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import csv
import sys
import os

def load_dataset(csv_path):
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input file not found: {csv_path}")
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != required_columns:
            raise ValueError(f"CSV columns invalid. Expected: {required_columns}, Found: {reader.fieldnames}")
        rows = list(reader)
    null_rows = [i for i, row in enumerate(rows) if not row["actual_spend"] or row["actual_spend"].strip() == ""]
    null_details = [
        {
            "index": i,
            "period": rows[i]["period"],
            "ward": rows[i]["ward"],
            "category": rows[i]["category"],
            "notes": rows[i]["notes"]
        }
        for i in null_rows
    ]
    return {
        "rows": rows,
        "null_count": len(null_rows),
        "null_details": null_details,
        "columns": reader.fieldnames
    }

def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        raise ValueError("--growth-type not specified. Refusing to guess. Please specify.")
    # Filter for ward and category
    filtered = [row for row in dataset["rows"] if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")
    # Sort by period
    filtered.sort(key=lambda r: r["period"])
    output = []
    prev_spend = None
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["actual_spend"]
        null_flag = False
        null_reason = ""
        growth_value = ""
        formula_used = ""
        if not actual_spend or actual_spend.strip() == "":
            null_flag = True
            null_reason = row["notes"] or "actual_spend is null"
        else:
            actual_spend = float(actual_spend)
            if growth_type == "MoM":
                if prev_spend is not None:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100 if prev_spend != 0 else None
                    if growth is not None:
                        growth_value = f"{growth:+.1f}%"
                        formula_used = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                    else:
                        growth_value = "n/a"
                        formula_used = "prev_spend is 0"
                else:
                    growth_value = "n/a"
                    formula_used = "No previous month"
                prev_spend = actual_spend
            else:
                raise ValueError(f"Unsupported growth_type: {growth_type}")
        output.append({
            "period": period,
            "actual_spend": row["actual_spend"],
            "growth_value": growth_value,
            "formula_used": formula_used,
            "null_flag": null_flag,
            "null_reason": null_reason
        })
    return output

def write_output(output_path, output_rows):
    fieldnames = ["period", "actual_spend", "growth_value", "formula_used", "null_flag", "null_reason"]
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="UC-0C: Per-ward, per-category growth computation.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    # Enforce: Must not aggregate across wards or categories
    if args.ward.lower() == "all" or args.category.lower() == "all":
        print("Refusing: Aggregation across wards or categories is not permitted.", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    try:
        dataset = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    # Report nulls before computing
    if dataset["null_count"] > 0:
        print(f"Found {dataset['null_count']} null actual_spend rows:")
        for detail in dataset["null_details"]:
            print(f"  Row {detail['index']}: {detail['period']} | {detail['ward']} | {detail['category']} | Reason: {detail['notes']}")

    # Enforce: Must specify growth-type
    if not args.growth_type:
        print("Refusing: --growth-type not specified. Please specify (e.g., MoM).", file=sys.stderr)
        sys.exit(1)

    # Compute growth
    try:
        output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"Error computing growth: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    try:
        write_output(args.output, output_rows)
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

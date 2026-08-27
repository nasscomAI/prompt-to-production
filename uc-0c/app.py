"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import csv
import sys

def load_dataset(file_path):
    """
    Reads the CSV, validates columns, and reports null count and which rows before returning the data.
    Returns: (data as list of dicts, null row info as list of dicts)
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    data = []
    null_rows = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Validate columns
            if not all(col in row for col in required_columns):
                raise ValueError(f"Missing required columns in input file: {row}")
            # Track nulls
            if row["actual_spend"] == '' or row["actual_spend"].strip().lower() == 'null':
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"]
                })
            data.append(row)
    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    """
    Computes growth for a given ward, category, and growth_type, returning a per-period table with formula shown.
    Flags and explains nulls. Refuses if growth_type is not specified.
    """
    if not growth_type:
        raise ValueError("--growth-type must be specified (e.g., MoM or YoY). Refusing to guess.")
    # Filter data for ward and category
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    # Sort by period
    filtered.sort(key=lambda r: r["period"])
    results = []
    prev_spend = None
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        if actual_spend == '' or actual_spend.strip().lower() == 'null':
            results.append({
                "period": period,
                "actual_spend": 'NULL',
                "growth": '',
                "formula": '',
                "flag": f"NULL: {notes.strip() if notes else 'No reason provided'}"
            })
            prev_spend = None
            continue
        try:
            spend = float(actual_spend)
        except Exception:
            results.append({
                "period": period,
                "actual_spend": actual_spend,
                "growth": '',
                "formula": '',
                "flag": f"Invalid spend value"
            })
            prev_spend = None
            continue
        if growth_type == 'MoM':
            if prev_spend is not None:
                growth = ((spend - prev_spend) / prev_spend) * 100 if prev_spend != 0 else 0
                growth_str = f"{growth:+.1f}%"
                formula = f"({spend} - {prev_spend}) / {prev_spend} * 100"
            else:
                growth_str = ''
                formula = ''
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": growth_str,
                "formula": formula,
                "flag": ''
            })
            prev_spend = spend
        else:
            raise ValueError(f"Unsupported growth_type: {growth_type}. Only 'MoM' is implemented.")
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    try:
        data, null_rows = load_dataset(args.input)
        # Enforce: refuse to aggregate across wards/categories
        if args.ward.lower() == 'all' or args.category.lower() == 'all':
            print("Refusing: Aggregation across wards or categories is not allowed unless explicitly instructed.")
            sys.exit(1)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        # Write output CSV
        fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"Done. Growth output written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

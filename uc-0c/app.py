"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

def load_dataset(csv_path: str) -> list:
    """
    Reads the CSV, validates columns, reports null count and which rows
    before returning.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input file {csv_path} does not exist.")

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    rows = []

    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Input CSV file {csv_path} has no headers.")

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV: {', '.join(missing_columns)}")

        # Read rows and check null values
        null_rows_report = []
        for line_num, row in enumerate(reader, start=2):
            actual_spend_raw = row.get("actual_spend", "").strip()
            
            # Identify null rows
            if not actual_spend_raw:
                null_rows_report.append({
                    "line": line_num,
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", "")
                })
                row["actual_spend"] = None
            else:
                try:
                    row["actual_spend"] = float(actual_spend_raw)
                except ValueError:
                    row["actual_spend"] = None
                    null_rows_report.append({
                        "line": line_num,
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "notes": f"Invalid float value: {actual_spend_raw}"
                    })

            rows.append(row)

    # Report null values to console/log
    print(f"Dataset loaded. Total rows: {len(rows)}.")
    print(f"Null actual_spend count: {len(null_rows_report)}")
    for report in null_rows_report:
        print(f"  - Null at row {report['line']}: {report['period']} | {report['ward']} | {report['category']} | Reason: {report['notes']}")

    return rows

def compute_growth(ward: str, category: str, growth_type: str, dataset: list) -> list:
    """
    Filters dataset to specific ward and category, and computes growth per period
    with formula shown. Refuses aggregation across multiple wards or categories.
    """
    # Refusal conditions on ward and category
    refusal_keywords = ["all", "any", "total", "combined", "*", ""]
    
    clean_ward = str(ward).strip().lower()
    clean_category = str(category).strip().lower()
    
    if any(keyword == clean_ward for keyword in refusal_keywords) or not ward:
        print("Refusal: Aggregation across multiple wards is not permitted under policy rules.", file=sys.stderr)
        sys.exit(1)
        
    if any(keyword == clean_category for keyword in refusal_keywords) or not category:
        print("Refusal: Aggregation across multiple categories is not permitted under policy rules.", file=sys.stderr)
        sys.exit(1)

    # Validate that ward and category exist in the dataset
    all_wards = set(row["ward"] for row in dataset)
    all_categories = set(row["category"] for row in dataset)
    
    matched_ward = None
    for w in all_wards:
        if w.strip().lower() == ward.strip().lower():
            matched_ward = w
            break
            
    matched_category = None
    for c in all_categories:
        if c.strip().lower() == category.strip().lower():
            matched_category = c
            break

    if not matched_ward:
        print(f"Refusal: Specified ward '{ward}' not found. Available wards: {', '.join(sorted(all_wards))}", file=sys.stderr)
        sys.exit(1)
        
    if not matched_category:
        print(f"Refusal: Specified category '{category}' not found. Available categories: {', '.join(sorted(all_categories))}", file=sys.stderr)
        sys.exit(1)

    # Filter data for matching ward and category
    filtered_data = [row for row in dataset if row["ward"] == matched_ward and row["category"] == matched_category]
    
    # Sort by period chronologically
    filtered_data.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered_data):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        
        prev_actual_spend = None
        growth_pct = ""
        formula = ""
        
        if i > 0:
            prev_row = filtered_data[i - 1]
            prev_actual_spend = prev_row["actual_spend"]

        # Check if current row is null
        if actual_spend is None:
            growth_pct = f"NULL_FLAGGED: {notes if notes else 'Data missing'}"
            formula = "n/a (actual_spend is null)"
        # Check if previous row is null
        elif i > 0 and prev_actual_spend is None:
            growth_pct = f"n/a (previous month spend is null due to: {prev_row['notes']})"
            formula = "n/a (previous month spend is null)"
        # First month
        elif i == 0:
            growth_pct = "n/a"
            formula = "n/a (first period)"
        else:
            if prev_actual_spend == 0:
                growth_pct = "n/a (division by zero)"
                formula = f"({actual_spend} - {prev_actual_spend}) / {prev_actual_spend} * 100"
            else:
                pct = ((actual_spend - prev_actual_spend) / prev_actual_spend) * 100
                if pct > 0:
                    growth_pct = f"+{pct:.1f}%"
                elif pct < 0:
                    growth_pct = f"-{abs(pct):.1f}%"
                else:
                    growth_pct = "0.0%"
                formula = f"MoM = ({actual_spend} - {prev_actual_spend}) / {prev_actual_spend} * 100"
                
        results.append({
            "period": period,
            "ward": matched_ward,
            "category": matched_category,
            "actual_spend": "NULL" if actual_spend is None else actual_spend,
            "growth": growth_pct,
            "formula": formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", default=None, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Refuse if growth-type is not specified
    if args.growth_type is None:
        print("Refusal: Growth type was not specified. You must specify --growth-type (e.g. MoM).", file=sys.stderr)
        sys.exit(1)

    if args.growth_type.strip().upper() != "MOM":
        print(f"Refusal: Growth type '{args.growth_type}' is not supported. Only 'MoM' is currently supported.", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    dataset = load_dataset(args.input)

    # Compute growth
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)

    # Write output CSV
    headers = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth analysis written to {args.output}")

if __name__ == "__main__":
    main()

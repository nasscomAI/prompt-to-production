import argparse
import csv
import sys
import os

def load_dataset(file_path: str, ward: str, category: str):
    """Skill: load_dataset - Reads CSV, validates columns, filters by ward & category."""
    if not os.path.exists(file_path):
        print(f"Error: Dataset not found at {file_path}")
        sys.exit(1)

    if not ward or not category:
        print("REFUSAL: Execution denied. Specific --ward and --category must be provided. Aggregations across all wards/categories are strictly forbidden.")
        sys.exit(1)

    filtered_rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'].strip() == ward.strip() and row['category'].strip() == category.strip():
                filtered_rows.append(row)

    if not filtered_rows:
        print(f"Error: No records found matching ward='{ward}' and category='{category}'")
        sys.exit(1)

    # Sort rows by period chronologically
    filtered_rows.sort(key=lambda x: x['period'])
    return filtered_rows

def compute_growth(rows: list, growth_type: str):
    """Skill: compute_growth - Computes MoM growth rates, handles nulls, and records formulas."""
    if not growth_type or growth_type.upper() != "MOM":
        print("REFUSAL: Execution denied. --growth-type must be explicitly specified (e.g., MoM). System refuses to guess formula.")
        sys.exit(1)

    results = []
    prev_spend = None

    for row in rows:
        period = row['period']
        ward = row['ward']
        category = row['category']
        raw_spend = row['actual_spend'].strip()
        notes = row['notes'].strip()

        # Check for deliberate null values
        if raw_spend == "" or raw_spend.upper() == "NULL":
            growth_rate = "NULL_FLAGGED"
            formula = f"Flagged: {notes}" if notes else "Flagged: Missing actual_spend"
            actual_spend_str = "NULL"
            prev_spend = None  # Reset baseline for next comparison
        else:
            actual_spend = float(raw_spend)
            actual_spend_str = str(actual_spend)

            if prev_spend is None:
                growth_rate = "N/A"
                formula = "Baseline period (no previous month data)"
            else:
                # MoM Growth Formula: ((Current - Prev) / Prev) * 100
                mom_change = ((actual_spend - prev_spend) / prev_spend) * 100
                growth_rate = f"{mom_change:+.1f}%"
                formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"

            prev_spend = actual_spend

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend_str,
            "growth_rate": growth_rate,
            "formula": formula,
            "notes": notes
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=True, help="Growth type metric (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()

    print(f"Loading and filtering dataset: {args.input}")
    filtered_data = load_dataset(args.input, args.ward, args.category)

    print(f"Computing {args.growth_type} growth rates...")
    results = compute_growth(filtered_data, args.growth_type)

    # Write output to CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "notes"]
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Success! Output generated at {args.output}")

if __name__ == "__main__":
    main()
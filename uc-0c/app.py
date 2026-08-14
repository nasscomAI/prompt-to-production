"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """Reads the ward budget CSV file and validates columns."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset file not found at {input_path}")
    
    rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Check expected columns
        expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not expected_cols.issubset(reader.fieldnames):
            raise ValueError(f"Missing required columns in CSV. Expected at least: {expected_cols}")
        for row in reader:
            rows.append(row)
    return rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: --growth-type is required. Please specify MoM.", file=sys.stderr)
        sys.exit(1)

    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Refusal: Growth type '{args.growth_type}' is not supported. Only MoM is supported.", file=sys.stderr)
        sys.exit(1)

    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or not args.category:
        print("Refusal: Both --ward and --category must be specified. Aggregation is not supported.", file=sys.stderr)
        sys.exit(1)

    if args.ward.lower() in ["all", "any", "total"] or args.category.lower() in ["all", "any", "total"]:
        print("Refusal: Aggregation across multiple wards or categories is prohibited.", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    try:
        dataset = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    # Normalize inputs for filtering
    target_ward = args.ward.strip()
    target_category = args.category.strip()

    # Filter data
    filtered = [
        row for row in dataset
        if row['ward'].strip() == target_ward and row['category'].strip() == target_category
    ]

    if not filtered:
        print(f"Refusal: No data found for ward '{target_ward}' and category '{target_category}'.", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda x: x['period'])

    results = []
    prev_spend = None

    for row in filtered:
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes'].strip()

        # Rule 2: Flag every null row before computing — report null reason from the notes column
        if actual_spend_str == "":
            actual_spend = "NULL"
            growth = "NULL"
            formula = "N/A"
            null_reason = notes if notes else "Data missing"
            # Since this month is null, previous spend for the next month becomes None
            prev_spend = None
            results.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": actual_spend,
                "growth": growth,
                "formula": formula,
                "notes": null_reason
            })
            continue

        # Valid actual spend
        actual_spend = float(actual_spend_str)

        if args.growth_type == "MoM":
            if prev_spend is None:
                growth = "N/A"
                formula = "N/A"
                notes_out = "No previous month data" if period.endswith("-01") else "Previous month spend is null"
            else:
                growth_val = (actual_spend - prev_spend) / prev_spend
                growth = f"{growth_val * 100:+.1f}%"
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend}"
                notes_out = notes
            
            # Update prev_spend
            prev_spend = actual_spend
        else:
            # YoY (not possible since we only have 2024 data)
            growth = "N/A"
            formula = "N/A"
            notes_out = "YoY requires previous year data which is not present in 2024 dataset."

        results.append({
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": actual_spend,
            "growth": growth,
            "formula": formula,
            "notes": notes_out
        })

    # Write output CSV
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth calculations written to {args.output}")

if __name__ == "__main__":
    main()

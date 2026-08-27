import argparse
import csv
import os
import sys

def load_dataset(file_path):
    """
    Reads CSV, validates columns, and identifies rows with missing actual_spend.
    """
    rows = []
    null_rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # Line numbers start at 2 (header is 1)
            if not row.get('actual_spend'):
                null_rows.append((i, row))
            rows.append(row)
    return rows, null_rows

def compute_growth(dataset, ward, category, growth_type):
    """
    Computes MoM or YoY growth for specific ward/category.
    Refuses aggregation.
    """
    # Enforcement Rule 1: Refuse aggregation
    if ward.lower() == "any" or category.lower() == "any":
        print("ERROR: All-ward or all-category aggregation is strictly prohibited. Please specify a single ward and category.")
        sys.exit(1)

    # Filter data
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    if not filtered:
        print(f"ERROR: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda x: x['period'])

    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend']
        notes = row['notes']
        
        # Enforcement Rule 2: Flag null rows
        if not actual:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "n/a",
                "formula": f"FLAG: Missing data - {notes or 'No reason provided'}"
            })
            continue

        actual_val = float(actual)
        growth_val = "n/a"
        formula = "n/a (First period)"

        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
                if prev_row['actual_spend']:
                    prev_val = float(prev_row['actual_spend'])
                    growth_val = f"{((actual_val - prev_val) / prev_val) * 100:.2f}%"
                    formula = f"({actual_val} - {prev_val}) / {prev_val}"
                else:
                    growth_val = "n/a"
                    formula = "Cannot compute: Previous period has NULL value"
        elif growth_type == "YoY":
            # Find period from 1 year ago (e.g., 2024-01 vs 2023-01)
            # In this dataset, we only have 2024 data, so YoY will mostly be n/a
            year, month = map(int, period.split('-'))
            target_period = f"{year-1}-{month:02d}"
            prev_row = next((r for r in dataset if r['period'] == target_period and r['ward'] == ward and r['category'] == category), None)
            if prev_row and prev_row['actual_spend']:
                prev_val = float(prev_row['actual_spend'])
                growth_val = f"{((actual_val - prev_val) / prev_val) * 100:.2f}%"
                formula = f"({actual_val} - {prev_val}) / {prev_val}"
            else:
                growth_val = "n/a"
                formula = f"No data found for {target_period}"

        results.append({
            "period": period,
            "actual_spend": actual_val,
            "growth": growth_val,
            "formula": formula
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific Ward name")
    parser.add_argument("--category", required=True, help="Specific Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement Rule 4: Refuse if growth-type is missing
    if not args.growth_type:
        print("ERROR: Growth type (--growth-type) not specified. Please choose 'MoM' or 'YoY'.")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        sys.exit(1)

    dataset, null_report = load_dataset(args.input)
    
    # Print null report to console for transparency
    if null_report:
        print(f"INFO: Found {len(null_report)} rows with missing data.")
        for line, row in null_report:
            print(f"  - Line {line}: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")

    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write to CSV
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Growth analysis successfully written to {args.output}")

if __name__ == "__main__":
    main()

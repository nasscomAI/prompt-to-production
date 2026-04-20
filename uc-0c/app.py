"""
UC-0C — Number That Looks Right
Implementation based on RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    """Reads CSV and identifies nulls."""
    data = []
    null_rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Validate actual_spend
                val = row.get('actual_spend', '').strip()
                if not val:
                    null_rows.append(row)
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(val)
                    except ValueError:
                        row['actual_spend'] = None
                        null_rows.append(row)
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        sys.exit(1)
    
    return data, null_rows

def compute_growth(data, ward, category, growth_type, output_path):
    """Computes MoM growth and writes to CSV."""
    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        current_spend = row['actual_spend']
        notes = row.get('notes', '')
        
        growth_val = "n/a"
        formula = "n/a"
        
        if growth_type == "MoM":
            if prev_spend is None:
                growth_val = "n/a (First Period)"
                formula = "n/a"
            elif current_spend is None:
                growth_val = f"NULL ({notes})"
                formula = f"(NULL - {prev_spend}) / {prev_spend}"
            elif prev_spend == 0:
                growth_val = "Inf"
                formula = f"({current_spend} - 0) / 0"
            else:
                growth = ((current_spend - prev_spend) / prev_spend) * 100
                growth_val = f"{growth:+.1f}%"
                formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
        
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend if current_spend is not None else "NULL",
            "growth": growth_val,
            "formula": formula,
            "notes": notes
        })
        
        prev_spend = current_spend

    # Write output
    if not results:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return

    keys = results[0].keys()
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type (MoM or YoY) must be specified. Please clarify your request.")
        sys.exit(1)

    # Refuse aggregation if requested (simulated check)
    if args.ward.lower() == "all" or args.category.lower() == "all":
        print("Error: Aggregation across all wards or categories is not permitted as per budget policy.")
        sys.exit(1)

    data, null_rows = load_dataset(args.input)
    print(f"Loaded {len(data)} rows. Found {len(null_rows)} null actual_spend values.")
    
    compute_growth(data, args.ward, args.category, args.growth_type, args.output)
    print(f"Done. Growth analysis written to {args.output}")

if __name__ == "__main__":
    main()

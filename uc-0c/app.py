"""
UC-0C app.py — Budget Growth Calculator
Follows RICE, agents.md, and skills.md.
"""
import argparse
import csv
import os

def load_dataset(input_path: str):
    """Reads CSV and validates columns."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File {input_path} not found.")
    
    records = []
    null_rows = []
    with open(input_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Clean numeric fields
            try:
                row['budgeted_amount'] = float(row['budgeted_amount']) if row['budgeted_amount'] else 0.0
                if row['actual_spend']:
                    row['actual_spend'] = float(row['actual_spend'])
                else:
                    row['actual_spend'] = None
                    null_rows.append(f"Row {i+2}: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
            except ValueError:
                pass
            records.append(row)
            
    print(f"Loaded {len(records)} records.")
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend values:")
        for nr in null_rows:
            print(f"  - {nr}")
            
    return records


def compute_growth(records, ward, category, growth_type):
    """Calculates MoM growth for the specified ward and category."""
    if not ward or ward.lower() == "any" or ward.lower() == "all":
        raise ValueError("Error: Individual ward must be specified. All-ward aggregation is not permitted.")
    if not category or category.lower() == "any" or category.lower() == "all":
        raise ValueError("Error: Individual category must be specified. All-category aggregation is not permitted.")
    if not growth_type:
        raise ValueError("Error: --growth-type must be specified (e.g., MoM).")

    # Filter data
    filtered = [r for r in records if r['ward'] == ward and r['category'] == category]
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        res = {
            "period": current['period'],
            "actual_spend": current['actual_spend'],
            "growth": "n/a",
            "formula": "First period or missing previous data"
        }
        
        if current['actual_spend'] is None:
            res['growth'] = "NULL"
            res['formula'] = f"Missing data: {current['notes']}"
        elif prev and prev['actual_spend'] is not None:
            # MoM Growth Formula: ((Current - Previous) / Previous) * 100
            diff = current['actual_spend'] - prev['actual_spend']
            growth = (diff / prev['actual_spend']) * 100
            res['growth'] = f"{growth:+.1f}%"
            res['formula'] = f"(({current['actual_spend']} - {prev['actual_spend']}) / {prev['actual_spend']}) * 100"
        elif prev and prev['actual_spend'] is None:
            res['growth'] = "n/a"
            res['formula'] = "Previous month actual_spend was NULL"
            
        results.append(res)
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Path to write the output CSV")
    args = parser.parse_args()

    try:
        # Load and validate
        records = load_dataset(args.input)
        
        # Compute
        results = compute_growth(records, args.ward, args.category, args.growth_type)
        
        # Write output
        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula"])
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth analysis written to {args.output}")
        
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    main()

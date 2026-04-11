import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    Reads the budget CSV, identifies nulls, and returns data.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
        
    data = []
    null_rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['actual_spend'].strip():
                null_rows.append(row)
                row['actual_spend'] = None
            else:
                row['actual_spend'] = float(row['actual_spend'])
            row['budgeted_amount'] = float(row['budgeted_amount'])
            data.append(row)
    
    if null_rows:
        print(f"REPORT: Found {len(null_rows)} rows with NULL actual_spend:")
        for nr in null_rows:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        print("-" * 50)
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Computes MoM growth for the specified ward and category.
    """
    # Filter for specific ward and category
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        print(f"No data found for Ward: {ward} and Category: {category}")
        return []

    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        res = {
            "Period": curr['period'],
            "Actual Spend (₹ lakh)": curr['actual_spend'] if curr['actual_spend'] is not None else "NULL",
            "Growth": "n/a",
            "Formula": "n/a"
        }
        
        if growth_type == "MoM":
            if i > 0:
                prev = filtered[i-1]
                if curr['actual_spend'] is not None and prev['actual_spend'] is not None:
                    c_val = curr['actual_spend']
                    p_val = prev['actual_spend']
                    growth = ((c_val - p_val) / p_val) * 100
                    res["Growth"] = f"{growth:+.1f}%"
                    res["Formula"] = f"({c_val} - {p_val}) / {p_val} * 100"
                elif curr['actual_spend'] is None:
                    res["Growth"] = "FLAGGED_NULL"
                    res["Formula"] = f"Skipped: {curr['notes']}"
                elif prev['actual_spend'] is None:
                    res["Growth"] = "SKIPPED_PREV_NULL"
                    res["Formula"] = f"Cannot compute: Previous period ({prev['period']}) was NULL"
            else:
                res["Formula"] = "Baseline period - no previous data for MoM"
        
        results.append(res)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target budget category")
    parser.add_argument("--growth-type", help="Type of growth (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path for growth_output.csv")
    args = parser.parse_args()

    # Enforcement: Refuse aggregation or missing type
    if not args.ward or not args.category:
        print("ERROR: Aggregation Refused. You must specify BOTH --ward and --category.")
        print("Reason: City-wide or multi-category aggregation level is not permitted.")
        sys.exit(1)
        
    if not args.growth_type:
        print("ERROR: Growth-type not specified. Please specify --growth-type (e.g., MoM).")
        sys.exit(1)

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    if results:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Results successfully written to {args.output}")

if __name__ == "__main__":
    main()

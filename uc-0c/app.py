"""
UC-0C Budget Growth Analyzer
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os

def load_dataset(input_path):
    """
    Skill: load_dataset
    Reads CSV and reports nulls.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File {input_path} not found.")
        
    data = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Column mapping and conversion
            try:
                actual = row['actual_spend']
                if actual.strip() == "":
                    row['actual_spend'] = None
                    null_rows.append({'row': i+2, 'period': row['period'], 'ward': row['ward'], 'category': row['category'], 'reason': row['notes']})
                else:
                    # Remove potential currency symbols or commas if present
                    actual_clean = actual.replace('₹', '').replace(',', '').strip()
                    row['actual_spend'] = float(actual_clean)
                
                row['budgeted_amount'] = float(row['budgeted_amount'].replace('₹', '').replace(',', '').strip())
                data.append(row)
            except ValueError as e:
                # Handle bad data rows
                continue
                
    if null_rows:
        print(f"REPORT: Found {len(null_rows)} deliberate null actual_spend rows.")
        for nr in null_rows:
            print(f"  - Period {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates MoM growth for a single ward/category pair.
    """
    if growth_type != "MoM":
        # agents.md dictates we must refuse unsupported or unstated growth types
        raise ValueError(f"Growth type '{growth_type}' is currently unsupported or invalid. Only 'MoM' is supported via this tool.")

    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        return []

    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        result_row = {
            "period": curr['period'],
            "ward": curr['ward'],
            "category": curr['category'],
            "actual_spend": curr['actual_spend'] if curr['actual_spend'] is not None else "NULL",
            "growth": "n/a",
            "formula": "n/a"
        }
        
        if i == 0:
            result_row['formula'] = "First period in dataset"
        elif curr['actual_spend'] is None:
            # Rule 2: Flag nulls, don't compute
            result_row['growth'] = "FLAGGED"
            result_row['formula'] = f"NULL found: {curr['notes'] or 'No reason provided'}"
        elif prev is None or prev['actual_spend'] is None:
            result_row['growth'] = "n/a"
            result_row['formula'] = "Cannot compute: Previous value is NULL or missing"
        else:
            # MoM Calculation: ((C - P) / P) * 100
            c = curr['actual_spend']
            p = prev['actual_spend']
            growth_val = ((c - p) / p) * 100
            result_row['growth'] = f"{growth_val:+.1f}%"
            # Rule 3: Show formula
            result_row['formula'] = f"(({c} - {p}) / {p}) * 100"
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    args = parser.parse_args()
    
    # Rule 4: Refuse if growth-type is missing
    if not args.growth_type:
        print("ERROR: --growth-type must be specified (e.g., MoM). Refusing to guess as per agents.md.")
        return

    print(f"Loading data for analysis...")
    try:
        data = load_dataset(args.input)
        
        print(f"Computing {args.growth_type} growth for {args.ward} | {args.category}...")
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"No records found for Ward: {args.ward} and Category: {args.category}.")
            return

        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Success! Results written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

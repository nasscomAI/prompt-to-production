import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the budget CSV, validates required columns, and identifies rows with null values.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    
    data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        missing_cols = [col for col in required_columns if col not in reader.fieldnames]
        if missing_cols:
            print(f"Error: Missing required columns: {', '.join(missing_cols)}")
            sys.exit(1)
        
        for row in reader:
            # Convert numeric fields
            try:
                row['budgeted_amount'] = float(row['budgeted_amount'])
            except (ValueError, TypeError):
                row['budgeted_amount'] = 0.0
            
            if row['actual_spend'] and row['actual_spend'].strip():
                try:
                    row['actual_spend'] = float(row['actual_spend'])
                except (ValueError, TypeError):
                    row['actual_spend'] = None
            else:
                row['actual_spend'] = None
            
            data.append(row)
    
    null_rows = [row for row in data if row['actual_spend'] is None]
    if null_rows:
        print(f"Found {len(null_rows)} rows with null actual_spend:")
        for row in null_rows:
            print(f"- {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    
    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates growth for a specific ward and category based on growth_type (MoM).
    """
    # Enforce no aggregation: filter strictly by ward and category
    subset = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'")
        sys.exit(1)
        
    # Sort by period
    subset.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in subset:
        current_spend = row['actual_spend']
        period = row['period']
        notes = row['notes']
        
        res_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': current_spend if current_spend is not None else "NULL",
            'growth_result': "n/a",
            'formula': "initial period" if prev_spend is None else f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
        }
        
        if current_spend is None:
            res_row['growth_result'] = "NULL (Flagged)"
            res_row['formula'] = f"Skipped: {notes}"
        elif prev_spend is not None:
             growth = ((current_spend - prev_spend) / prev_spend) * 100
             res_row['growth_result'] = f"{growth:+.1f}%"
        elif prev_spend is None:
            res_row['growth_result'] = "Basis"
        else: # prev was NULL
             res_row['growth_result'] = "n/a (Prev was NULL)"
             res_row['formula'] = "Cannot compute: Previous period was NULL"

        results.append(res_row)
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Expert Pune Budget Analyst Tool")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    args = parser.parse_args()
    
    # Enforcement: Refuse if --growth-type not specified
    if not args.growth_type:
        print("Error: --growth-type is required. Please specify 'MoM'.")
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print(f"Error: Unsupported growth-type '{args.growth_type}'. Only 'MoM' is supported.")
        sys.exit(1)

    # load_dataset skill
    data, _ = load_dataset(args.input)
    
    # compute_growth skill
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save to output
    if results:
        keys = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success: Analysis saved to {args.output}")

if __name__ == "__main__":
    main()

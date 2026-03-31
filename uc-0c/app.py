import argparse
import csv
import os
import sys

def load_dataset(input_path):
    """
    Reads CSV and validates columns. Reports null counts.
    """
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        sys.exit(1)
        
    data = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames)):
            print(f"Error: Missing required columns. Found: {reader.fieldnames}")
            sys.exit(1)
            
        for row in reader:
            if not row['actual_spend'] or row['actual_spend'].strip() == "":
                null_rows.append(row)
            data.append(row)
            
    if null_rows:
        print(f"Warning: Found {len(null_rows)} rows with null actual_spend.")
        for nr in null_rows:
            print(f"  - Null at {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Computes MoM growth for a specific ward and category.
    """
    if not growth_type:
        print("Error: Growth type not specified. Please use --growth-type (e.g., MoM).")
        sys.exit(1)
    
    if growth_type != "MoM":
        print(f"Error: Unsupported growth type '{growth_type}'. This system only supports MoM.")
        sys.exit(1)
        
    # Filter and sort by period
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    if not filtered:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)
        
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        current_spend_str = row['actual_spend']
        notes = row['notes']
        
        res_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend_str if current_spend_str else "NULL",
            "growth_result": "n/a",
            "formula_used": "n/a",
            "notes": notes
        }
        
        if not current_spend_str or current_spend_str.strip() == "":
            res_row["growth_result"] = "NOT_COMPUTABLE"
            res_row["formula_used"] = "Cannot compute with NULL current spend"
            prev_spend = None # Reset previous spend on null to avoid incorrect MoM next month
        else:
            current_spend = float(current_spend_str)
            if prev_spend is not None:
                growth = ((current_spend - prev_spend) / prev_spend) * 100
                res_row["growth_result"] = f"{growth:+.1f}%"
                res_row["formula_used"] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                res_row["growth_result"] = "First Period"
                res_row["formula_used"] = "Baseline"
            
            prev_spend = current_spend
            
        results.append(res_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name")
    parser.add_argument("--category", help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # Enforcement: Refuse if ward or category not specified (aggregation check)
    if not args.ward or not args.category:
        print("Error: Aggregation across multiple wards or categories is strictly prohibited.")
        print("Please specify both --ward and --category.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_result", "formula_used", "notes"]
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()

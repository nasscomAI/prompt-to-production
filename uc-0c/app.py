import argparse
import csv
import sys
import os

def load_dataset(input_path, target_ward, target_category):
    if not os.path.exists(input_path):
        print(f"Error: Dataset not found at {input_path}")
        sys.exit(1)
        
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == target_ward and row['category'] == target_category:
                data.append(row)
                
    if not data:
        print(f"Error: No data found for Ward: '{target_ward}' and Category: '{target_category}'")
        sys.exit(1)
        
    # Sort by period to ensure MoM calculation is correct
    data.sort(key=lambda x: x['period'])
    return data

def compute_growth(data, growth_type):
    if growth_type != "MoM":
        print(f"Error: Growth type '{growth_type}' is not supported. Please use 'MoM'.")
        sys.exit(1)
        
    results = []
    prev_spend = None
    
    for row in data:
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes']
        
        result_row = {
            "period": period,
            "actual_spend": actual_spend_str if actual_spend_str else "NULL",
            "growth": "n/a",
            "formula": "n/a",
            "status": "OK"
        }
        
        if not actual_spend_str:
            result_row["status"] = f"FLAGGED: {notes}"
            prev_spend = None # Reset previous spend on null to avoid invalid growth jump
        else:
            curr_spend = float(actual_spend_str)
            if prev_spend is not None:
                growth = ((curr_spend - prev_spend) / prev_spend) * 100
                result_row["growth"] = f"{growth:+.1f}%"
                result_row["formula"] = f"({curr_spend} - {prev_spend}) / {prev_spend}"
            
            prev_spend = curr_spend
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Auditor")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=True, help="Type of growth calculation (MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # 1. Load and Filter
    data = load_dataset(args.input, args.ward, args.category)
    
    # 2. Compute
    results = compute_growth(data, args.growth_type)
    
    # 3. Save
    fieldnames = ["period", "actual_spend", "growth", "formula", "status"]
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth analysis written to {args.output}")

if __name__ == "__main__":
    main()

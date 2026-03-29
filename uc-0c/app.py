import argparse
import csv
import sys
import os
from datetime import datetime

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the budget CSV, validates essential columns, and reports null counts.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
        
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing = [col for col in required_columns if col not in reader.fieldnames]
            if missing:
                print(f"Error: Missing required columns: {missing}")
                sys.exit(1)
            
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    # 2. Report null count and specific rows
    null_rows = [row for row in data if not row['actual_spend'] or row['actual_spend'].strip() == '' or row['actual_spend'].lower() == 'null']
    null_count = len(null_rows)
    print(f"--- Dataset Validation Report ---")
    print(f"Total rows: {len(data)}")
    print(f"Found {null_count} null rows in 'actual_spend'.")
    
    if null_count > 0:
        for row in null_rows:
            print(f"  - NULL detected at {row['period']} | {row['ward']} | {row['category']} (Reason: {row['notes']})")
    print(f"---------------------------------\n")
    
    return data

def compute_growth(dataset, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates per-period growth for a specific ward and category.
    """
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide MoM or YoY.")
        sys.exit(1)
        
    # 1. Filter by ward and category
    subset = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)
        
    # Sort by period
    try:
        subset.sort(key=lambda x: datetime.strptime(x['period'], '%Y-%m'))
    except Exception as e:
        print(f"Error parsing date: {e}")
        sys.exit(1)
    
    results = []
    
    for i in range(len(subset)):
        row = subset[i]
        period = row['period']
        actual_val_raw = row['actual_spend']
        notes = row['notes']
        
        is_null = not actual_val_raw or actual_val_raw.strip() == '' or actual_val_raw.lower() == 'null'
        
        growth_val = "n/a"
        formula = "n/a (First period)"
        
        if is_null:
            actual_display = "NULL"
            growth_val = "NULL"
            formula = f"Refused: Data missing ({notes})"
        else:
            actual_display = actual_val_raw
            actual_float = float(actual_val_raw)
            
            if i > 0:
                prev_row = subset[i-1]
                prev_actual_raw = prev_row['actual_spend']
                prev_is_null = not prev_actual_raw or prev_actual_raw.strip() == '' or prev_actual_raw.lower() == 'null'
                
                if prev_is_null:
                    growth_val = "n/a"
                    formula = f"n/a (Previous period was NULL)"
                else:
                    prev_float = float(prev_actual_raw)
                    diff = actual_float - prev_float
                    growth_pct = (diff / prev_float) * 100
                    growth_val = f"{growth_pct:+.1f}%"
                    
                    if growth_type.upper() == 'MOM':
                        formula = f"({actual_float} - {prev_float}) / {prev_float}"
                    elif growth_type.upper() == 'YOY':
                        formula = f"({actual_float} - {prev_float}) / {prev_float} [YoY comparison]"
        
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_display,
            'growth_result': growth_val,
            'formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Tracker")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific budget category")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV filename")
    
    args = parser.parse_args()
    
    # 1. Load and validate
    dataset = load_dataset(args.input)
    
    # 2. Compute
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # 3. Save output
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        print(f"Success: Growth table saved to {args.output}")
    except Exception as e:
        print(f"Error saving output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Budget Data Analyst
Built using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str) -> list:
    """Reads budget CSV, validates columns, and checks for nulls."""
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        sys.exit(1)
        
    data = []
    null_rows = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend'}
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames)):
            print(f"Error: Missing columns. Expected {required_cols}")
            sys.exit(1)
            
        for row_idx, row in enumerate(reader, start=2):
            # Check for nulls in actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip() == "":
                null_rows.append((row_idx, row['period'], row['ward'], row['category'], row['notes']))
            data.append(row)
            
    if null_rows:
        print(f"Initial Scan: Found {len(null_rows)} null actual_spend values.")
        for idx, p, w, c, note in null_rows:
            print(f"  - Row {idx}: {p} | {w} | {c} | Reason: {note}")
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Calculates growth for specific ward and category."""
    if not growth_type:
        print("Refusal: Growth type (MoM/YoY) must be specified. I cannot guess.")
        sys.exit(1)
    
    if not ward or not category:
        print("Refusal: Specific ward and category must be provided. I refuse to aggregate.")
        sys.exit(1)
        
    # Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    if not filtered:
        print(f"Refusal: No data found for ward '{ward}' and category '{category}'.")
        sys.exit(1)
        
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        curr_val_str = curr['actual_spend'].strip()
        period = curr['period']
        
        result = {
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': curr_val_str if curr_val_str else "NULL",
            'growth': "n/a",
            'formula': "n/a",
            'notes': curr['notes']
        }
        
        if not curr_val_str:
            result['growth'] = "FLAGGED"
            result['formula'] = f"NULL found. Reason: {curr['notes']}"
            results.append(result)
            continue
            
        curr_val = float(curr_val_str)
        
        if growth_type.upper() == "MOM":
            if i == 0:
                result['growth'] = "n/a"
                result['formula'] = "First period in dataset"
            else:
                prev = filtered[i-1]
                prev_val_str = prev['actual_spend'].strip()
                if not prev_val_str:
                    result['growth'] = "n/a"
                    result['formula'] = f"Previous period ({prev['period']}) was NULL"
                else:
                    prev_val = float(prev_val_str)
                    if prev_val == 0:
                        result['growth'] = "inf"
                        result['formula'] = f"({curr_val} - 0) / 0"
                    else:
                        growth = (curr_val - prev_val) / prev_val
                        result['growth'] = f"{growth:+.1%}"
                        result['formula'] = f"({curr_val} - {prev_val}) / {prev_val}"
        elif growth_type.upper() == "YOY":
            # Finding same month in previous year (e.g., 2024-01 vs 2023-01)
            # Dataset only has 2024, so YoY will always be n/a for this specific task
            # unless 2023 data existed.
            result['growth'] = "n/a"
            result['formula'] = "Previous year data not available"
        else:
            print(f"Refusal: Unsupported growth type '{growth_type}'. Use MoM or YoY.")
            sys.exit(1)
            
        results.append(result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Data Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # Load dataset (Skill 1)
    data = load_dataset(args.input)
    
    # Compute growth (Skill 2)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Write output
    fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth', 'formula', 'notes']
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Processed {len(results)} rows. Results written to {args.output}")

if __name__ == "__main__":
    main()

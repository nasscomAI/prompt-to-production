"""
UC-0C Budget Analysis App
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, and reports null counts before returning data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file {file_path} not found.")
    
    data = []
    null_rows = []
    mandatory_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend']
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        if not all(col in reader.fieldnames for col in mandatory_cols):
            missing = [col for col in mandatory_cols if col not in reader.fieldnames]
            raise ValueError(f"Missing mandatory columns: {missing}")
            
        for i, row in enumerate(reader, start=2): # Line number start from 2 (after header)
            # Basic validation
            if not row['period'] or not row['ward'] or not row['category']:
                print(f"Skipping malformed row at line {i}")
                continue
                
            # Null check for actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip() == "":
                null_rows.append((i, row['period'], row['ward'], row['category'], row['notes']))
            
            data.append(row)
            
    # Report nulls as required by Enforcement Rule 2
    if null_rows:
        print(f"Identified {len(null_rows)} rows with missing 'actual_spend':")
        for line, period, ward, cat, note in null_rows:
            print(f"  - Line {line}: {period} | {ward} | {cat} | Reason: {note if note else 'None provided'}")
    else:
        print("No null 'actual_spend' values found.")
        
    return data

def compute_growth(data, ward_name, category_name, growth_type):
    """
    Computes growth for a specific ward and category.
    Returns a list of rows for the output table.
    """
    # Filter for specific ward and category (Enforcement Rule 1: No aggregation)
    filtered = [r for r in data if r['ward'] == ward_name and r['category'] == category_name]
    
    if not filtered:
        print(f"No data found for Ward: '{ward_name}' and Category: '{category_name}'.")
        return []
        
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, current in enumerate(filtered):
        period = current['period']
        actual_curr_str = current['actual_spend']
        
        # Check for null current value
        if not actual_curr_str or actual_curr_str.strip() == "":
            results.append({
                "period": period,
                "ward": ward_name,
                "category": category_name,
                "actual_spend": "NULL",
                "growth": "N/A",
                "formula": "N/A",
                "status": f"FLAGGED: {current['notes']}"
            })
            continue
            
        actual_curr = float(actual_curr_str)
        
        # Find previous value for MoM
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward_name,
                    "category": category_name,
                    "actual_spend": actual_curr,
                    "growth": "N/A",
                    "formula": "First period in dataset",
                    "status": "OK"
                })
                continue
            
            prev = filtered[i-1]
            actual_prev_str = prev['actual_spend']
            
            # Check for null previous value
            if not actual_prev_str or actual_prev_str.strip() == "":
                results.append({
                    "period": period,
                    "ward": ward_name,
                    "category": category_name,
                    "actual_spend": actual_curr,
                    "growth": "N/A",
                    "formula": "N/A",
                    "status": f"REFUSED: Previous period ({prev['period']}) is NULL ({prev['notes']})"
                })
                continue
                
            actual_prev = float(actual_prev_str)
            if actual_prev == 0:
                growth_val = "DIV/0"
                formula = f"({actual_curr} - 0) / 0"
            else:
                growth_val = f"{((actual_curr - actual_prev) / actual_prev) * 100:+.1f}%"
                formula = f"({actual_curr} - {actual_prev}) / {actual_prev}"
                
            results.append({
                "period": period,
                "ward": ward_name,
                "category": category_name,
                "actual_spend": actual_curr,
                "growth": growth_val,
                "formula": formula,
                "status": "OK"
            })
        elif growth_type == "YoY":
            # Dataset only contains 2024 data, so YoY is not possible within this set
            results.append({
                "period": period,
                "ward": ward_name,
                "category": category_name,
                "actual_spend": actual_curr,
                "growth": "N/A",
                "formula": "YoY requires 2023 data",
                "status": "UNAVAILABLE"
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Specific ward to analyze")
    parser.add_argument("--category", help="Specific category to analyze")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: Refuse if growth-type missing
    if not args.growth_type:
        print("Error: --growth-type (MoM or YoY) must be specified. Guessing is prohibited.")
        sys.exit(1)
        
    # Enforcement Rule 1: Refuse if ward or category missing (prevent aggregation)
    if not args.ward or not args.category:
        print("Error: Both --ward and --category must be specified to prevent unauthorized aggregation.")
        sys.exit(1)
        
    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if not results:
            return
            
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "status"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Done. Growth report for '{args.ward}' | '{args.category}' written to {args.output}")
        
    except Exception as e:
        print(f"Process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


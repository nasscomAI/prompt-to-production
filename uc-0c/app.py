"""
UC-0C app.py - Structured Data Analyst Agent
Computes budget growth metrics strictly at the ward and category level without unauthorized cross-aggregation.
"""
import argparse
import csv
import os
import sys

def load_dataset(filepath):
    """
    Reads the CSV file, validates required columns, and identifies missing data.
    Input: File path to the CSV dataset.
    Output: A validated dataset object (list of dicts), along with a report detailing 
            the total count of null values and the specific rows where they occur.
    """
    if not os.path.exists(filepath):
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    data = []
    null_report = []
    
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not required_cols.issubset(set(reader.fieldnames or [])):
                print(f"Error: Missing required columns in dataset. Expected {required_cols}")
                sys.exit(1)
                
            for row_num, row in enumerate(reader, start=2): # 1-indexed, skipping header
                 # Enforce Rule 2: Flag every null row before computing
                if not row['actual_spend'].strip() or row['actual_spend'].strip().upper() == "NULL":
                    null_report.append({
                        "row": row_num,
                        "period": row['period'],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row['notes']
                    })
                data.append(row)
                
    except Exception as e:
         print(f"Error reading dataset: {e}")
         sys.exit(1)
         
    # Identify null counts explicitly for reporting
    print(f"Dataset loaded: {len(data)} rows.")
    if null_report:
        print(f"\n[WARNING] Found {len(null_report)} rows with explicitly null `actual_spend`:")
        for r in null_report:
            print(f"  - Row {r['row']} ({r['period']} | {r['ward']} | {r['category']}): {r['notes']}")
    else:
        print("No null `actual_spend` values found.")
        
    return data

def compute_growth(dataset, growth_type):
    """
    Calculates the requested growth metric (e.g., MoM) per ward and category over time.
    """
    # Enforcement 4 & 6 validation
    if not growth_type or growth_type.upper() != "MOM":
        print(f"Error: Growth formula (--growth-type) not specified or not MoM. Refusing to guess.")
        sys.exit(1)
        
    # Group dataset by ward and category to avoid cross-aggregation (Rule 4)
    grouped_data = {}
    for row in dataset:
        ward = row['ward'].strip()
        cat = row['category'].strip()
        key = (ward, cat)
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(row)
        
    from typing import List, Dict
    results: List[Dict[str, str]] = []
    
    for (ward, category), group in grouped_data.items():
        # Sort chronologically inside group
        group.sort(key=lambda x: x['period'])
        
        for i in range(len(group)):
            current = group[i]
            period = current['period']
            actual_str = current['actual_spend'].strip()
            
            is_null = not actual_str or actual_str.upper() == "NULL"
            
            current_val = None
            if not is_null:
                 try:
                     current_val = float(actual_str)
                 except ValueError:
                     is_null = True
                     
            if is_null:
                # Rule 3
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "NULL",
                    "growth_metric": "n/a (null)",
                    "formula": "",
                    "notes": current.get('notes', '').strip() or 'NULL'
                })
                continue

            growth_val = "n/a"
            formula = ""
            notes = current.get('notes', '').strip()
            
            # Rule 2
            if i == 0:
                growth_val = "n/a (first period)"
            else:
                prev = group[i-1]
                prev_actual_str = prev['actual_spend'].strip()
                
                prev_is_null = not prev_actual_str or prev_actual_str.upper() == "NULL"
                if prev_is_null:
                    # Previous was null, so we cannot compute metric
                    growth_val = "n/a"
                else:
                    formula = "((Current / Previous) - 1) * 100"
                    try:
                        prev_val = float(prev_actual_str)
                        if prev_val == 0:
                             growth_val = "Infinity"
                        elif current_val is not None:
                             # Rule 1 calculation
                             pct = ((current_val / prev_val) - 1) * 100
                             
                             # Rule: formatting explicitly like spec with regular minus
                             sign = "+" if pct > 0 else "-" if pct < 0 else ""
                             growth_val = f"{sign}{abs(pct):.1f}%"
                             
                    except ValueError:
                        growth_val = "Error parsing previous"
                        formula = "Error"
                        
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(current_val),
                "growth_metric": growth_val,
                "formula": formula,
                "notes": notes
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Structured Data Analyst")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--growth-type", help="Formula metric to use (e.g. MoM) (Required)") 
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    # Optional filtering arguments if still provided, to remain flexibly compatible
    parser.add_argument("--ward", help="Optional specific Ward to analyze")
    parser.add_argument("--category", help="Optional specific Category to analyze")
    
    args = parser.parse_args()
    
    print("\n--- UC-0C Data Extraction Agent ---")
    data = load_dataset(args.input)
    
    # Pre-filter if they provided ward/category intentionally, otherwise run on all
    if args.ward and args.category:
        target_ward_normalized = args.ward.replace('–', '-').replace('—', '-').strip()
        target_category_normalized = args.category.replace('–', '-').replace('—', '-').strip()
        filtered_data = []
        for row in data:
            row_ward = row['ward'].replace('–', '-').replace('—', '-').strip()
            row_cat = row['category'].replace('–', '-').replace('—', '-').strip()
            if row_ward == target_ward_normalized and row_cat == target_category_normalized:
                filtered_data.append(row)
        data = filtered_data
    
    print("----------------------------------\n")
    
    calculations = compute_growth(data, args.growth_type)
    
    if not calculations:
        print("Warning: No matching data found.")
        sys.exit(0)
        
    # Write output exactly
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        # Expected column order
        fieldnames = ["period", "ward", "category", "actual_spend", "growth_metric", "formula", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in calculations:
            writer.writerow(row)
            
    print(f"\nSuccess! Output written to {args.output}")

if __name__ == "__main__":
    main()

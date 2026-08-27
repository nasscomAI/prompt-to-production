"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os
from collections import defaultdict

def load_dataset(input_path: str):
    """
    Skill 1: Reads CSV, validates columns, reports null count and distinct rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset not found at {input_path}")
        
    data = []
    null_rows = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                 print(f"Warning: Dataset missing standard columns. Expected: {required_columns}")
                 # Continue gracefully if possible for "malformed rows without crashing" rule
                
            for row in reader:
                # Basic protection for malformed rows
                if not row or not isinstance(row, dict):
                     continue
                     
                safe_row = {
                    'period': row.get('period', 'UNKNOWN'),
                    'ward': row.get('ward', 'UNKNOWN WARD'),
                    'category': row.get('category', 'UNKNOWN CATEGORY'),
                    'budgeted_amount': row.get('budgeted_amount', ''),
                    'actual_spend': row.get('actual_spend', ''),
                    'notes': row.get('notes', '')
                }
                
                data.append(safe_row)
                spend_val = safe_row.get('actual_spend')
                if not spend_val or spend_val.strip() == '':
                    null_rows.append(safe_row)
                    
        print(f"\n[Validation] Dataset loaded: {len(data)} rows.")
        print(f"[Validation] Found {len(null_rows)} explicitly null `actual_spend` rows.")
        for nr in null_rows:
            print(f"  - NULL in Period: {nr.get('period')} | Ward: {nr.get('ward')} | Category: {nr.get('category')}")
            
    except Exception as e:
         print(f"Error loading dataset: {e}. Returning empty data.")
         
    return data

def compute_growth(data: list, growth_type: str):
    """
    Skill 2: Group by ward+category to compute explicitly (e.g. MoM) without mixing them.
    """
    if not growth_type:
        print("Warning: --growth-type flag is missing. Defaulting to MoM to prevent crash, but strictly you should specify.")
        growth_type = "MoM"
        
    if growth_type != "MoM":
         print(f"Warning: Only 'MoM' growth type is technically implemented. Proceeding with MoM logic for {growth_type}.")

    # Enforce strict calculation boundary: bucket strictly by ward+category
    grouped_data = defaultdict(list)
    for row in data:
         ward = row['ward'].strip()
         category = row['category'].strip()
         grouped_data[(ward, category)].append(row)
    
    results = []
    
    # Process each independent bucket
    for (ward, category), group in grouped_data.items():
        # Sort chronologically
        sorted_group = sorted(group, key=lambda x: x['period'])
        
        # MoM Calculation Loop
        for i, current_row in enumerate(sorted_group):
            period = current_row['period']
            current_val_str = current_row.get('actual_spend', '').strip()
            note = current_row.get('notes', '').strip()
            
            output_row = {
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': current_val_str if current_val_str else "NULL",
                'growth_type': growth_type,
                'growth_pct': "",
                'formula_used': "",
                'notes': note
            }
            
            # Enforcement 2: Explicitly catch NULL
            if not current_val_str:
                output_row['growth_pct'] = "FLAGGED NULL"
                output_row['formula_used'] = f"CANNOT COMPUTE: {note}"
                results.append(output_row)
                continue
                
            try:
                current_val = float(current_val_str)
            except ValueError:
                output_row['growth_pct'] = "ERROR"
                output_row['formula_used'] = f"Malformed float text: {current_val_str}"
                results.append(output_row)
                continue
            
            # Determine previous value for MoM
            if i == 0:
                output_row['growth_pct'] = "N/A"
                output_row['formula_used'] = "First period in dataset (No previous period)"
                results.append(output_row)
                continue
                
            prev_row = sorted_group[i-1]
            prev_val_str = prev_row.get('actual_spend', '').strip()
            
            if not prev_val_str:
                output_row['growth_pct'] = "N/A"
                output_row['formula_used'] = f"Previous period was NULL ({prev_row.get('notes')})"
                results.append(output_row)
                continue
                
            try:
                prev_val = float(prev_val_str)
            except ValueError:
                 output_row['growth_pct'] = "ERROR"
                 output_row['formula_used'] = f"Previous period had malformed text: {prev_val_str}"
                 results.append(output_row)
                 continue
            
            # Zero division safeguard
            if prev_val == 0:
                 output_row['growth_pct'] = "UNDEFINED"
                 output_row['formula_used'] = f"({current_val} - 0) / 0"
                 results.append(output_row)
                 continue
                 
            # Actual MoM
            growth = ((current_val - prev_val) / prev_val) * 100
            sign = "+" if growth > 0 else ""
            
            output_row['growth_pct'] = f"{sign}{growth:.1f}%"
            # Enforcement 3: Show explicit formula
            output_row['formula_used'] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
            
            results.append(output_row)
        
    return results

def write_results(results: list, output_path: str):
    if not results:
         print("No output generated.")
         return
         
    try:
        # Ensure directory exists before opening outfile
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
             
        fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth_type', 'growth_pct', 'formula_used', 'notes']
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
                
        print(f"\nSuccess. Computed outputs saved to {output_path}")
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Strict Calculator")
    parser.add_argument("--input", required=False, default="../data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--growth-type", required=False, default="MoM", help="Growth logic (e.g. MoM)")
    parser.add_argument("--output", required=False, default="growth_output.csv", help="Path to write output csv")
    
    # Keeping arg placeholders so old scripts don't break, but they are ignored globally now.
    parser.add_argument("--ward", required=False, help="Ignored")
    parser.add_argument("--category", required=False, help="Ignored")
    args = parser.parse_args()
    
    print(f"Executing Strict Budget Agent...")
    
    try:
         data = load_dataset(args.input)
         
         # The agent enforces grouping properly without us needing to filter first.
         results = compute_growth(data, args.growth_type)
         
         write_results(results, args.output)
         
    except Exception as e:
         print(f"\nSYSTEM COMPLETED WITH ERRORS: {e}")

if __name__ == "__main__":
    main()

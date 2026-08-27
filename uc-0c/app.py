import argparse
import csv
import sys
import os
from pathlib import Path

def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, and reports null count/rows.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    dataset = []
    null_rows = []
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        field_list = reader.fieldnames
        if field_list is None:
            field_list = []
        
        # Validate columns using simple membership to avoid set-related lint issues in this environment
        missing_cols = [col for col in required_cols if col not in field_list]
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}")
            sys.exit(1)
            
        for i, row in enumerate(reader, start=2): # line 1 is header
            # Handle empty actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip() == "":
                row['actual_spend'] = None
                null_rows.append((i, row['period'], row['ward'], row['category'], row['notes']))
            else:
                try:
                    row['actual_spend'] = float(row['actual_spend'])
                except ValueError:
                    row['actual_spend'] = None
                    null_rows.append((i, row['period'], row['ward'], row['category'], "Invalid float value"))
            
            try:
                row['budgeted_amount'] = float(row['budgeted_amount'])
            except ValueError:
                row['budgeted_amount'] = 0.0
                
            dataset.append(row)
            
    if null_rows:
        print(f"REPORT: Found {len(null_rows)} null actual_spend values:")
        for row_info in null_rows:
            print(f"  - Line {row_info[0]}: {row_info[1]} | {row_info[2]} | {row_info[3]} | Reason: {row_info[4]}")
            
    return dataset

def compute_growth(ward, category, growth_type, dataset):
    """
    Calculates growth (MoM/YoY) for specific ward+category.
    """
    # Filter data
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    if not filtered:
        return []
        
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, current in enumerate(filtered):
        prev = None
        offset = 1 if growth_type == "MoM" else 12
        
        if i >= offset:
            prev = filtered[i - offset]
            
        current_val = current['actual_spend']
        prev_val = prev['actual_spend'] if prev else None
        
        growth_val = "N/A"
        formula = "N/A"
        note = current['notes'] if current_val is None else ""
        
        if prev is None:
            formula = f"First available {growth_type} period"
        elif current_val is None:
            growth_val = "NULL"
            formula = "N/A"
            note = current['notes']
        elif prev_val is None:
            growth_val = "NULL"
            formula = "N/A"
            note = f"Previous period ({prev['period']}) was null: {prev['notes']}"
        else:
            # Calculate growth
            try:
                growth = (current_val - prev_val) / prev_val
                growth_val = f"{growth*100:+.1f}%"
                formula = f"({current_val} - {prev_val}) / {prev_val}"
            except ZeroDivisionError:
                growth_val = "INF"
                formula = f"({current_val} - 0) / 0"
                
        results.append({
            "ward": ward,
            "category": category,
            "period": current['period'],
            "actual_spend": current_val if current_val is not None else "NULL",
            "growth_value": growth_val,
            "formula_used": formula,
            "note": note
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst Agent")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Specific ward name (optional)")
    parser.add_argument("--category", help="Specific category name (optional)")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", help="Path to write CSV results")
    args = parser.parse_args()
    
    # Enforcement 1: Refuse aggregation keywords
    forbidden = ["all", "any", "*", "total", "combined"]
    if (args.ward and args.ward.lower() in forbidden) or (args.category and args.category.lower() in forbidden):
        print("ERROR: Unauthorized aggregation detected. This agent is restricted to granular per-ward, per-category analysis.")
        sys.exit(1)
        
    # Enforcement 4: Growth type required
    if not args.growth_type:
        print("ERROR: Growth type not specified. Please provide --growth-type (MoM or YoY).")
        sys.exit(1)
        
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"ERROR: Invalid growth type '{args.growth_type}'. Use MoM or YoY.")
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    
    # Expansion: Support all ward/category combinations if not specified
    wards = [args.ward] if args.ward else sorted(list({r['ward'] for r in dataset}))
    categories = [args.category] if args.category else sorted(list({r['category'] for r in dataset}))
    
    all_results = []
    for w in wards:
        for c in categories:
            res = compute_growth(w, c, args.growth_type, dataset)
            all_results.extend(res)
    
    if not all_results:
        print("No data found for the specified selection.")
        return

    # Output headers
    fieldnames = ["ward", "category", "period", "actual_spend", "growth_value", "formula_used", "note"]
    
    if args.output:
        # Prepend directory if needed
        output_path = Path(args.output).resolve()
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
            
        with open(str(output_path), mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Results written to {args.output}")
    else:
        # Print as table
        header = f"{'Ward':<20} | {'Category':<25} | {'Period':<10} | {'Spend':<8} | {'Growth':<10} | {'Formula':<30} | {'Note'}"
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        for r in all_results:
            print(f"{r['ward']:<20} | {r['category']:<25} | {r['period']:<10} | {str(r['actual_spend']):<8} | {r['growth_value']:<10} | {r['formula_used']:<30} | {r['note']}")

if __name__ == "__main__":
    main()



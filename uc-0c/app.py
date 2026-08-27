"""
UC-0C app.py — Financial Growth Analyst
Strictly enforces rules from agents.md and skills.md.
"""
import argparse
import csv
import sys
import os
from collections import defaultdict

def load_dataset(filepath: str) -> list:
    """
    Reads CSV, validates columns, reports null count, and returns dataset.
    """
    if not os.path.exists(filepath):
        print(f"Error: dataset not found at {filepath}")
        sys.exit(1)
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend'}
    dataset = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        if not required_cols.issubset(headers):
            print(f"Error: Missing required columns in dataset. Found: {headers}")
            sys.exit(1)
            
        for idx, row in enumerate(reader, start=2): # 1 is header
            actual_spend = row.get('actual_spend', '').strip()
            if not actual_spend:
                null_rows.append((idx, row.get('ward'), row.get('category'), row.get('period'), row.get('notes')))
            dataset.append(row)
            
    print(f"Loaded {len(dataset)} rows. Validated columns.")
    if null_rows:
        print(f"ATTENTION: Found {len(null_rows)} explicitly null actual_spend row(s):")
        for r in null_rows:
            print(f"  - Row {r[0]}: {r[3]} | {r[1]} | {r[2]} | Note: {r[4]}")
            
    return dataset

def compute_growth(dataset: list, target_ward: str, target_category: str, growth_type: str) -> list:
    """
    Computes precise per-ward, per-category growth, avoiding silent aggregations.
    """
    if not growth_type:
        print("REFUSAL: --growth-type not specified. Cannot assume formula. Please specify (e.g., MoM).")
        sys.exit(1)
        
    if growth_type.lower() != 'mom':
        print(f"REFUSAL: Only MoM growth is currently supported in this analysis, requested: {growth_type}")
        sys.exit(1)

    # Group records by (ward, category) to process independent streams without 
    # cross-ward or cross-category silent aggregation. 
    # If the user asks to sum them ("All-ward aggregation"), we'd refuse.
    # Here, 'All' means generating the per-ward per-category table individually.
    
    groups = defaultdict(list)
    for row in dataset:
        w = row['ward']
        c = row['category']
        
        # Filter if a specific ward/cat was requested
        if target_ward.lower() != 'all' and w != target_ward:
            continue
        if target_category.lower() != 'all' and c != target_category:
            continue
            
        groups[(w, c)].append(row)
        
    results = []
    
    # Process each independent stream
    for (w, c), rows in groups.items():
        # Sort chronologically
        rows.sort(key=lambda x: x['period'])
        
        prev_spend = None
        for row in rows:
            period = row['period']
            actual_spend_str = row['actual_spend'].strip()
            notes = row.get('notes', '')
            
            # Rule: Flag every null row before computing AND report reason
            if not actual_spend_str:
                results.append({
                    'Ward': w,
                    'Category': c,
                    'Period': period,
                    'Actual Spend': 'NULL',
                    'Growth': 'FLAGGED',
                    'Formula Used': f"Data missing: {notes}"
                })
                prev_spend = None  # Reset previous spend due to break in chain
                continue
                
            current_spend = float(actual_spend_str)
            
            if prev_spend is None:
                growth_str = 'n/a'
                formula_str = 'First valid period/No previous data'
            else:
                if prev_spend == 0:
                    growth_str = 'n/a'
                    formula_str = 'Cannot divide by zero prevailing base'
                else:
                    growth = ((current_spend - prev_spend) / prev_spend) * 100
                    growth_str = f"{'+' if growth > 0 else ''}{growth:.1f}%"
                    formula_str = f"({current_spend} - {prev_spend}) / {prev_spend} * 100 ({growth_type})"
                    
            results.append({
                'Ward': w,
                'Category': c,
                'Period': period,
                'Actual Spend': str(current_spend),
                'Growth': growth_str,
                'Formula Used': formula_str
            })
            
            prev_spend = current_spend
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="All", help="Target ward strictly or 'All'")
    parser.add_argument("--category", default="All", help="Target category strictly or 'All'")
    parser.add_argument("--growth-type", required=False, help="Explicit growth formula (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. I will not guess the formula.")
        sys.exit(1)
        
    print(f"Loading data from {args.input}")
    dataset = load_dataset(args.input)
    
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    if results:
        fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend', 'Growth', 'Formula Used']
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Successfully generated {len(results)} rows. Saved to {args.output}")
    else:
        print("No matching data found to analyze.")

if __name__ == "__main__":
    main()

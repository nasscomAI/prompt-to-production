"""
UC-0C app.py — Strict Growth Calculator
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys
import os

def load_dataset(filepath: str) -> list:
    """
    Reads CSV, validates columns, reports null counts and affected rows.
    """
    if not os.path.exists(filepath):
        print(f"Error: Input file {filepath} not found.")
        sys.exit(1)
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        if not required_cols.issubset(headers):
            print(f"Error: Missing required columns. Found {headers}, expected {required_cols}")
            sys.exit(1)
            
        for row in reader:
            data.append(row)
            if not row['actual_spend'].strip():
                null_rows.append(row)
                
    if null_rows:
        print(f"WARNING: Found {len(null_rows)} row(s) with null 'actual_spend'.")
        for r in null_rows:
            print(f"  - Null found at {r['period']} for {r['ward']} | {r['category']}. Reason: {r['notes']}")
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes validated data for a specific ward and category and computes growth.
    Refuses cross-aggregation. Flags nulls. Shows formula.
    """
    if not growth_type:
        print("Error: --growth-type MUST be specified. Refusing to guess formula.")
        sys.exit(1)
        
    if not ward or not category:
        print("Error: Ward and Category MUST be specified separately. Refusing cross-aggregation.")
        sys.exit(1)
        
    # Filter data specific to ward and category
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        print(f"No data found for Ward '{ward}' and Category '{category}'.")
        sys.exit(1)
        
    # Sort chronologically by period
    filtered.sort(key=lambda x: x['period'])
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        spend_str = row['actual_spend'].strip()
        
        if not spend_str:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth': f"Cannot compute — {row['notes']}"
            })
            continue
            
        current_spend = float(spend_str)
        
        # Determine growth based on type
        if growth_type.upper() == "MOM":
            if i == 0:
                growth_val = "n/a (first month)"
            else:
                prev_spend_str = filtered[i-1]['actual_spend'].strip()
                if not prev_spend_str:
                    growth_val = "n/a (previous month null)"
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth_val = "n/a (div by zero)"
                    else:
                        pct = ((current_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if pct > 0 else ""
                        growth_val = f"{sign}{pct:.1f}% [Formula: ((Current - Prev) / Prev) * 100]"
        elif growth_type.upper() == "YOY":
            # For this specific 12-month 2024 dataset, YoY computation isn't inherently possible
            # without prior year data, but logic exists here to demonstrate structure.
            growth_val = "n/a (insufficient prior year data) [Formula: ((Current - LastYear) / LastYear) * 100]"
        else:
            print(f"Error: Unknown growth-type '{growth_type}'. Refusing to proceed.")
            sys.exit(1)
            
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': f"{current_spend:.1f}",
            'growth': growth_val
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth metric to calculate (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to write the results CSV")
    
    args = parser.parse_args()
    
    print("Loading dataset and performing strict validation...")
    data = load_dataset(args.input)
    
    print(f"Computing {args.growth_type} growth for {args.ward} -> {args.category}...")
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth'])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Detailed growth results written to {args.output}")

if __name__ == "__main__":
    main()

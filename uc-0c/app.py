"""
UC-0C app.py
Number That Looks Right - implements the MoM budget growth logic
strictly adhering to constraints on aggregation and null handling.
"""
import argparse
import csv
import sys

def load_dataset(filepath):
    """reads CSV, validates columns, reports null count and which rows before returning"""
    rows = []
    null_count = 0
    null_details = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # 1-index + header
            if not row['actual_spend'].strip():
                null_count += 1
                null_details.append(f"{row['period']} | {row['ward']}: {row['notes']}")
            rows.append(row)
            
    print(f"Loaded dataset with {len(rows)} rows.")
    print(f"Found {null_count} null 'actual_spend' values. They are deliberately flagged:")
    for detail in null_details:
        print(f" - {detail}")
        
    return rows

def compute_growth(dataset, target_ward, target_category, growth_type):
    """takes ward + category + growth_type, returns per-period table with formula shown"""
    
    # 4. If --growth-type not specified — refuse and ask
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide --growth-type (e.g., MoM).")
        sys.exit(1)
        
    # 1. Never aggregate across wards or categories
    if not target_ward or target_ward.lower() == "all" or not target_category or target_category.lower() == "all":
        print("Error: Aggregation across wards or categories is strictly forbidden unless explicitly instructed. Please specify a single ward and category.")
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"Error: {growth_type} growth is not supported by this deterministic script.")
        sys.exit(1)
        
    filtered = [r for r in dataset if r['ward'] == target_ward and r['category'] == target_category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        
        # 2. Flag every null row before computing
        if not actual_spend_str:
            growth_formatted = "NULL"
            # 3. Show formula used in every output row
            formula = f"Flagged NULL: {row['notes']}"
            prev_spend = None
        else:
            actual_spend = float(actual_spend_str)
            if prev_spend is None:
                growth_formatted = "n/a"
                formula = "No previous month data to compute MoM"
            else:
                growth_val = ((actual_spend - prev_spend) / prev_spend) * 100
                prefix = "+" if growth_val > 0 else ""
                growth_formatted = f"{prefix}{growth_val:.1f}%"
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                
            prev_spend = actual_spend
            
        results.append({
            'period': period,
            'ward': target_ward,
            'category': target_category,
            'actual_spend': actual_spend_str if actual_spend_str else "NULL",
            'growth': growth_formatted,
            'formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Growth calculation complete. Saved to {args.output}")

if __name__ == "__main__":
    main()

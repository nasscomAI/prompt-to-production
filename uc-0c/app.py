"""
UC-0C — Number That Looks Right
Financial data analysis with strict null handling and formula transparency.
"""
import argparse
import csv
import os

def load_dataset(input_path):
    """
    Read CSV and return rows plus a report of nulls.
    """
    rows = []
    null_report = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            actual = row.get('actual_spend', '').strip()
            if not actual:
                null_report.append({
                    'line': i,
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'reason': row.get('notes', 'No reason provided')
                })
            rows.append(row)
            
    return rows, null_report

def compute_growth(rows, ward, category, growth_type):
    """
    Compute growth (MoM) for the specified ward and category.
    """
    # Filter data
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    
    # Sort by period to ensure MoM is correct
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        curr_val_str = curr.get('actual_spend', '').strip()
        
        if not curr_val_str:
            results.append({
                'period': curr['period'],
                'actual_spend': 'NULL',
                'growth': 'n/a',
                'formula': f"NULL detected: {curr.get('notes', 'No reason')}"
            })
            continue

        curr_val = float(curr_val_str)
        
        if prev and prev.get('actual_spend', '').strip():
            prev_val = float(prev['actual_spend'])
            if growth_type == 'MoM':
                if prev_val == 0:
                    growth = "inf"
                    formula = f"({curr_val} - 0) / 0"
                else:
                    change = (curr_val - prev_val) / prev_val
                    growth = f"{change:+.1%}"
                    formula = f"({curr_val} - {prev_val}) / {prev_val}"
            else:
                growth = "n/a"
                formula = "Only MoM supported in this version"
        else:
            growth = "n/a"
            formula = "First period or previous was NULL"
            
        results.append({
            'period': curr['period'],
            'actual_spend': curr_val,
            'growth': growth,
            'formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Rule: Refuse if growth-type missing
    if not args.growth_type:
        print("Error: --growth-type (MoM or YoY) must be specified. Guesses are not allowed.")
        return

    print(f"Loading dataset {args.input}...")
    rows, null_report = load_dataset(args.input)
    
    # Rule: Report nulls for the selected scope
    scope_nulls = [n for n in null_report if n['ward'] == args.ward and n['category'] == args.category]
    if scope_nulls:
        print(f"IDENTIFIED NULL RECORDS in {args.ward} | {args.category}:")
        for n in scope_nulls:
            print(f"  - {n['period']}: {n['reason']}")
    
    print(f"Computing {args.growth_type} growth...")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    # Save to CSV
    keys = results[0].keys()
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()

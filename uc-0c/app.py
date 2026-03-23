"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    dataset = []
    null_rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset.append(row)
            if not row.get('actual_spend') or row.get('actual_spend').strip() == '':
                null_rows.append(row)
                
    if null_rows:
        print(f"WARNING: Discovered {len(null_rows)} null actual_spend rows.")
        for nr in null_rows:
            print(f"  - Null found at {nr['period']}, {nr['ward']}, {nr['category']}. Reason: {nr['notes']}")
            
    return dataset

def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    if not ward or not category:
        print("ERROR: Refusal - Aggregation across wards or categories without explicit filtering is forbidden. Please provide both --ward and --category.")
        sys.exit(1)
        
    if not growth_type or growth_type.upper() != 'MOM':
        print("ERROR: Refusal - Unspecified or unsupported growth type. Only 'MoM' is supported currently.")
        sys.exit(1)

    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        spend_str = row['actual_spend']
        notes = row.get('notes', '')
        
        if not spend_str or spend_str.strip() == '':
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'growth_pct': 'NULL',
                'formula': f"Cannot compute: {notes}"
            })
            prev_spend = None # Reset previous spend since the sequence is broken
            continue
            
        current_spend = float(spend_str)
        
        if prev_spend is None:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'growth_pct': 'n/a',
                'formula': "No previous period data to compare"
            })
        else:
            growth = ((current_spend - prev_spend) / prev_spend) * 100
            formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            sign = '+' if growth > 0 else ''
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'growth_pct': f"{sign}{growth:.1f}%",
                'formula': formula
            })
            
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to filter")
    parser.add_argument("--category", required=False, help="Specific category to filter")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'growth_pct', 'formula'])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()

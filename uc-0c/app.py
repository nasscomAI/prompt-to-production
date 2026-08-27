import argparse
import csv
import sys

def load_dataset(filepath):
    rows = []
    null_indices = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows.append(row)
            if not row.get('actual_spend', '').strip():
                null_indices.append((i + 1, row.get('period'), row.get('ward'), row.get('category')))
    
    if null_indices:
        print(f"WARNING: Found {len(null_indices)} null actual_spend rows:")
        for idx, period, ward, cat in null_indices:
            print(f"  Row {idx}: {period} | {ward} | {cat}")
    
    return rows

def compute_growth(rows, ward, category, growth_type):
    filtered = [r for r in rows if r.get('ward') == ward and r.get('category') == category]
    filtered.sort(key=lambda x: x.get('period', ''))
    
    if not filtered:
        raise ValueError(f"No data found for ward={ward}, category={category}")
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row.get('period')
        actual_spend_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '').strip()
        
        if not actual_spend_str:
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'growth_pct': 'NULL',
                'formula': 'N/A',
                'notes': notes if notes else 'actual_spend is null'
            })
            continue
        
        actual_spend = float(actual_spend_str)
        
        if prev_spend is None:
            results.append({
                'period': period,
                'actual_spend': actual_spend,
                'growth_pct': 'N/A',
                'formula': 'N/A (first period)',
                'notes': notes
            })
        else:
            growth = ((actual_spend - prev_spend) / prev_spend) * 100
            results.append({
                'period': period,
                'actual_spend': actual_spend,
                'growth_pct': round(growth, 2),
                'formula': f'({actual_spend} - {prev_spend}) / {prev_spend} * 100',
                'notes': notes
            })
        
        prev_spend = actual_spend
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Compute budget growth')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--ward', required=True, help='Ward name')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=True, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file')
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth_pct', 'formula', 'notes'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
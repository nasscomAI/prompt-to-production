"""
UC-0C — Budget Growth Calculator
Computes month-over-month spend growth from ward-level budget CSV.
"""
import argparse
import csv
import sys

def load_dataset(file_path: str) -> list:
    """Reads CSV, validates columns, reports null count."""
    rows = []
    null_count = 0
    null_rows = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            actual = row.get('actual_spend', '').strip()
            if actual == '' or actual.lower() == 'null':
                null_count += 1
                null_rows.append(f"Row {i}: {row.get('period')} {row.get('ward')} {row.get('category')} - {row.get('notes', 'No reason')}")
                row['actual_spend'] = None
            else:
                row['actual_spend'] = float(actual)
            rows.append(row)
    
    print(f"Loaded {len(rows)} rows, {null_count} null values:")
    for nr in null_rows:
        print(f"  - {nr}")
    
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Compute growth per period for specified ward/category."""
    if growth_type not in ('MoM', 'YoY'):
        raise ValueError(f"Invalid growth_type: {growth_type}. Must be MoM or YoY.")
    
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend']
        null_flag = ''
        null_reason = ''
        growth_pct = ''
        formula = ''
        
        if actual is None:
            null_flag = 'NULL'
            null_reason = row.get('notes', 'No data')
            growth_pct = 'n/a'
            formula = 'Skipped - null value'
        elif i == 0:
            growth_pct = 'n/a'
            formula = 'No prior period'
        else:
            prev = filtered[i-1]['actual_spend']
            if prev is None:
                growth_pct = 'n/a'
                formula = 'Skipped - prior period null'
            else:
                change = actual - prev
                if growth_type == 'MoM':
                    growth_pct = (change / prev) * 100 if prev != 0 else 0
                    formula = f"(({actual} - {prev}) / {prev}) * 100"
                elif growth_type == 'YoY':
                    if i >= 12:
                        prev_y = filtered[i-12]['actual_spend']
                        if prev_y:
                            growth_pct = ((actual - prev_y) / prev_y) * 100
                            formula = f"(({actual} - {prev_y}) / {prev_y}) * 100"
        
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual if actual else 'NULL',
            'growth_pct': f"{growth_pct:.1f}%" if isinstance(growth_pct, float) else growth_pct,
            'formula': formula,
            'null_flag': null_flag,
            'null_reason': null_reason
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_pct', 'formula', 'null_flag', 'null_reason']
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Output written to {args.output}")
    print(f"Total periods: {len(results)}")

if __name__ == "__main__":
    main()
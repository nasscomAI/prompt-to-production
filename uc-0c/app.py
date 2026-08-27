# -*- coding: utf-8 -*-
"""
UC-0C - Number That Looks Right
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    data = []
    nulls = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            data.append(row)
            if not row.get('actual_spend') or row.get('actual_spend').strip() == '':
                nulls.append((row['period'], row['ward'], row['category'], row['notes']))
    
    print(f"Loaded {len(data)} rows.")
    if nulls:
        print(f"Warning: Found {len(nulls)} deliberate null actual_spend values.")
        for n in nulls:
            print(f"  - {n[0]} · {n[1]} · {n[2]} (Reason: {n[3]})")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    if not ward or ward.lower() == 'any' or not category or category.lower() == 'any':
        print("SYSTEM REFUSAL: Aggregation across wards or categories is strictly prohibited unless explicitly instructed.")
        sys.exit(1)
        
    if not growth_type:
        print("SYSTEM REFUSAL: Growth type not specified. Never guess.")
        sys.exit(1)
        
    if growth_type.lower() != 'mom':
        print("SYSTEM REFUSAL: Only MoM growth is supported in this implementation.")
        sys.exit(1)
        
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        spend_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '').strip()
        period = row['period']
        
        if not spend_str:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth': 'FLAGGED',
                'formula': 'N/A',
                'notes': f"Null flagged. Reason: {notes}"
            })
            prev_spend = None
            continue
            
        current_spend = float(spend_str)
        
        if prev_spend is None:
            growth = "N/A"
            formula = "N/A (No previous month)"
        else:
            growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
            growth = f"{growth_pct:+.1f}%"
            formula = f"({current_spend} - {prev_spend}) / {prev_spend}"
            
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': current_spend,
            'growth': growth,
            'formula': formula,
            'notes': notes
        })
        
        prev_spend = current_spend
        
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UC-0C Budget Growth Calculator')
    parser.add_argument('--input',  required=True, help='Path to budget CSV')
    parser.add_argument('--ward', required=False, help='Ward name')
    parser.add_argument('--category', required=False, help='Category name')
    parser.add_argument('--growth-type', required=False, help='Growth calculation type (e.g., MoM)')
    parser.add_argument('--output', required=True, help='Path to write growth output CSV')
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
            
    print(f"Done. Growth output written to {args.output}")

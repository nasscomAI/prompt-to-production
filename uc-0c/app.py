import argparse
import csv
import sys

def load_dataset(filepath):
    data = []
    nulls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['actual_spend'] or row['actual_spend'].strip().upper() == 'NULL':
                nulls.append(row)
            data.append(row)
            
    print(f"Validation: Loaded {len(data)} rows.")
    if nulls:
        print(f"Warning: Found {len(nulls)} null rows:")
        for n in nulls:
            print(f"  - {n['period']} | {n['ward']} | {n['category']} | Reason: {n.get('notes', 'N/A')}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    if not ward or ward.lower() == 'all':
        raise ValueError("REFUSED: Cannot aggregate across wards. Please specify a single ward.")
    if not category or category.lower() == 'all':
        raise ValueError("REFUSED: Cannot aggregate across categories. Please specify a single category.")
    if not growth_type:
        raise ValueError("REFUSED: Growth type not specified. Never guess.")
        
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        
        if not row['actual_spend'] or row['actual_spend'].strip().upper() == 'NULL':
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': 'FLAGGED NULL',
                'formula': 'N/A'
            })
            continue
            
        current = float(row['actual_spend'])
        growth = "N/A"
        formula = "N/A"
        
        if growth_type.upper() == 'MOM':
            if i > 0:
                prev_row = filtered[i-1]
                if prev_row['actual_spend'] and prev_row['actual_spend'].strip().upper() != 'NULL':
                    prev = float(prev_row['actual_spend'])
                    if prev > 0:
                        pct = ((current - prev) / prev) * 100
                        growth = f"{pct:+.1f}%"
                        formula = f"({current} - {prev}) / {prev} * 100"
        
        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': current,
            'growth': growth,
            'formula': formula
        })
        
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=False)
    parser.add_argument('--category', required=False)
    parser.add_argument('--growth-type', required=False)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not results:
                f.write("No data found.\n")
            else:
                writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth', 'formula'])
                writer.writeheader()
                writer.writerows(results)
                
        print(f"Growth calculation completed. Output written to {args.output}")
        
    except ValueError as e:
        print(e)
        sys.exit(1)

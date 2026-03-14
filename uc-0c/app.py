import argparse
import csv
import sys

def load_dataset(input_path: str):
    data = []
    null_count = 0
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            val = row.get('actual_spend', '').strip()
            if not val or val.lower() == 'null':
                null_count += 1
                row['actual_spend'] = None
            else:
                row['actual_spend'] = float(val)
            data.append(row)
    print(f"Loaded dataset: {len(data)} rows. Found {null_count} null 'actual_spend' values.")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    if not ward or ward.lower() == 'all' or not category or category.lower() == 'all':
        raise ValueError("REFUSAL: Cannot aggregate across wards or categories without explicit instructions.")
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified. Refusing to guess.")
        
    filtered = [d for d in data if d['ward'] == ward and d['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        spend = row['actual_spend']
        period = row['period']
        notes = row.get('notes', '')
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': spend if spend is not None else 'NULL',
            'growth': 'n/a',
            'formula': 'n/a',
            'flag': ''
        }
        
        if spend is None:
            result_row['flag'] = f"NULL FLAGGED - Reason: {notes}"
            prev_spend = None # break chain
            results.append(result_row)
            continue
            
        if growth_type.upper() == 'MOM':
            if prev_spend is not None and prev_spend != 0:
                growth_pct = ((spend - prev_spend) / prev_spend) * 100
                result_row['growth'] = f"{growth_pct:+.1f}%"
                result_row['formula'] = f"(({spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                result_row['formula'] = "Insufficient previous data"
        else:
            result_row['formula'] = f"Unsupported growth {growth_type}"
            
        prev_spend = spend
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    
    try:
        args = parser.parse_args()
    except:
        print("REFUSAL: Missing required arguments. Please ensure --growth-type among others is specified.")
        sys.exit(1)
        
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print("No data matched the criteria.")
            sys.exit(0)
            
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'flag'])
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Done. Growth output written to {args.output}")
        
    except ValueError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

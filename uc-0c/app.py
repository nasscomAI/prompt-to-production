import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_count = 0
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            missing = required_cols - set(reader.fieldnames or [])
            if missing:
                print(f"Error: Missing columns in dataset: {missing}")
                sys.exit(1)
            
            for row in reader:
                val = row['actual_spend'].strip()
                if not val or val.upper() == 'NULL' or val.upper() == 'NONE':
                    null_count += 1
                    null_rows.append(f"{row['period']} | {row['ward']} | {row['category']} -> {row['notes']}")
                data.append(row)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    print(f"--- Dataset Loaded ---")
    print(f"Total rows: {len(data)}")
    if null_count > 0:
        print(f"Found {null_count} rows with NULL actual_spend:")
        for r in null_rows:
            print(f"  - {r}")
    print("----------------------\n")
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Takes ward, category, and growth_type to calculate per-period growth showing the formula used.
    """
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered)):
        curr = filtered[i]
        period = curr['period']
        notes = curr['notes'].strip()
        val_str = curr['actual_spend'].strip()
        
        is_null = not val_str or val_str.upper() in ('NULL', 'NONE')
        
        if is_null:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth': f"Flagged NULL (Reason: {notes})",
                'formula': 'Not Computed'
            })
            continue

        curr_spend = float(val_str)
        growth_str = ""
        formula = ""
        
        if growth_type.upper() == "MOM":
            if i == 0:
                growth_str = "n/a (first period)"
                formula = "n/a"
            else:
                prev_str = filtered[i-1]['actual_spend'].strip()
                if not prev_str or prev_str.upper() in ('NULL', 'NONE'):
                    growth_str = "n/a (prev period is NULL)"
                    formula = "current / NULL"
                else:
                    prev_spend = float(prev_str)
                    if prev_spend == 0:
                        growth_str = "n/a (div by zero)"
                        formula = f"({curr_spend} - 0) / 0"
                    else:
                        pct = ((curr_spend - prev_spend) / prev_spend) * 100
                        growth_str = f"{pct:+.1f}%"
                        if notes:
                            growth_str += f" ({notes})"
                        formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"
                        
        elif growth_type.upper() == "YOY":
            y, m = period.split('-')
            prev_period = f"{int(y)-1}-{m}"
            prev_row = next((r for r in filtered if r['period'] == prev_period), None)
            
            if not prev_row:
                growth_str = "n/a (no prior year data)"
                formula = "n/a"
            else:
                prev_str = prev_row['actual_spend'].strip()
                if not prev_str or prev_str.upper() in ('NULL', 'NONE'):
                    growth_str = "n/a (prev year is NULL)"
                    formula = "current / NULL"
                else:
                    prev_spend = float(prev_str)
                    if prev_spend == 0:
                        growth_str = "n/a (div by zero)"
                        formula = f"({curr_spend} - 0) / 0"
                    else:
                        pct = ((curr_spend - prev_spend) / prev_spend) * 100
                        growth_str = f"{pct:+.1f}%"
                        if notes:
                            growth_str += f" ({notes})"
                        formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"
        
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': curr_spend,
            'growth': growth_str,
            'formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Strict Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # 1. Enforcement: Refuse aggregation 
    if not args.ward or not args.category:
        print("ERROR: Refusal Condition Met - Must specify both --ward and --category.")
        print("Never aggregate across wards or categories unless explicitly instructed.")
        sys.exit(1)
        
    # 4. Enforcement: Refuse if --growth-type not specified
    if not args.growth_type:
        print("ERROR: Refusal Condition Met - --growth-type must be specified.")
        print("Do not guess the growth calculation type.")
        sys.exit(1)
        
    if args.growth_type.upper() not in ["MOM", "YOY"]:
        print("ERROR: --growth-type must be either MoM or YoY.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula'])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print(f"Successfully processed. Output saved to {args.output}")

if __name__ == "__main__":
    main()

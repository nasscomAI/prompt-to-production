import argparse
import sys
import csv

def load_dataset(filepath: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    data = []
    null_count = 0
    null_rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                print(f"Error: Missing columns. Found: {reader.fieldnames}")
                sys.exit(1)
                
            for i, row in enumerate(reader, start=2):
                val = row['actual_spend'].strip()
                if not val:
                    null_count += 1
                    null_rows.append((row['period'], row['ward'], row['category'], row['notes']))
                data.append(row)
                
        # Reporting nulls explicitly as required by agent skills definition
        print(f"Dataset loaded. Found {null_count} null actual_spend rows:")
        for r in null_rows:
            print(f"  - {r[0]} | {r[1]} | {r[2]} -> Note: {r[3]}")
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        sys.exit(1)
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes ward, category, and growth_type, returns per-period table with formula shown."""
    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category:
        print("REFUSED: Cannot aggregate across wards or categories unless explicitly instructed. Missing ward or category.")
        sys.exit(1)
        
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        out_row = {
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': row['actual_spend'],
            'growth': 'n/a',
            'formula': 'n/a',
            'flag': ''
        }
        
        val_str = row['actual_spend'].strip()
        if not val_str:
            # Enforcement Rule 2: Flag every null row before computing
            out_row['flag'] = f"NULL DETECTED: {row['notes']}"
            results.append(out_row)
            prev_spend = None
            continue
            
        curr_spend = float(val_str)
        
        if prev_spend is not None:
            # Enforcement Rule 3: Show formula used in every output row alongside the result
            if prev_spend == 0:
                out_row['growth'] = 'undefined'
                out_row['formula'] = f"({curr_spend} - 0) / 0 * 100"
            else:
                growth_pct = ((curr_spend - prev_spend) / prev_spend) * 100
                sign = '+' if growth_pct > 0 else ''
                out_row['growth'] = f"{sign}{growth_pct:.1f}%"
                out_row['formula'] = f"({curr_spend} - {prev_spend}) / {prev_spend} * 100"
                
        prev_spend = curr_spend
        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Type of growth calculation")
    parser.add_argument("--output", required=True, help="Path for output csv")
    args = parser.parse_args()

    # Enforcement Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("REFUSED: --growth-type not specified. Please specify MoM or YoY parameters. Never guessing.")
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print("REFUSED: Only MoM growth type is supported in this implementation.")
        sys.exit(1)

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print(f"Success. Wrote results to {args.output}")

if __name__ == "__main__":
    main()

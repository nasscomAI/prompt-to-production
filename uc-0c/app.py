import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing required columns. Found: {reader.fieldnames}")
            
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: Data file {filepath} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)
        
    null_rows = []
    for row in data:
        if not row['actual_spend'].strip():
            null_rows.append(row)
            
    print(f"Dataset loaded. Total rows: {len(data)}")
    print(f"Found {len(null_rows)} null actual_spend rows:")
    for r in null_rows:
        print(f" - {r['period']} | {r['ward']} | {r['category']} | Reason: {r.get('notes', 'N/A')}")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Computes growth per period using the specified growth type.
    """
    # Enforce no aggregation across wards or categories
    if not ward or not category or ward.lower() == 'all' or category.lower() == 'all':
        print("Error: Never aggregate across wards or categories unless explicitly instructed — refuse if asked.")
        sys.exit(1)
        
    filtered = [d for d in data if d['ward'] == ward and d['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row.get('notes', '').strip()
        
        # Rule 2: Flag every null row before computing
        if not actual_str:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': 'NULL',
                'MoM Growth': f"FLAGGED NULL: {notes}",
                'Formula': "N/A"
            })
            continue
            
        current = float(actual_str)
        
        if i == 0:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': str(current),
                'MoM Growth': 'N/A (First period)',
                'Formula': 'N/A'
            })
            continue
            
        if growth_type.lower() == 'mom':
            prev_row = filtered[i-1]
            prev_str = prev_row['actual_spend'].strip()
            
            if not prev_str:
                results.append({
                    'Ward': ward,
                    'Category': category,
                    'Period': period,
                    'Actual Spend': str(current),
                    'MoM Growth': 'N/A (Previous period was NULL)',
                    'Formula': 'N/A'
                })
                continue
                
            prev = float(prev_str)
            if prev == 0:
                growth_str = "N/A"
                formula = f"({current} - 0) / 0"
            else:
                growth_val = ((current - prev) / prev) * 100
                growth_str = f"{growth_val:+.1f}%"
                if notes:
                    growth_str += f" ({notes})"
                formula = f"({current} - {prev}) / {prev} * 100"
                
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': str(current),
                'MoM Growth': growth_str,
                'Formula': formula
            })
        else:
            print(f"Error: Unsupported growth type '{growth_type}'")
            sys.exit(1)
            
    return results

def main():
    parser = argparse.ArgumentParser(description="Compute budget growth metrics.")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--ward', help="Ward name")
    parser.add_argument('--category', help="Category name")
    parser.add_argument('--growth-type', help="Growth type e.g., MoM")
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    # Parse known args so we can manually catch missing optional-seeming args to fulfill enforcement rules
    args, _ = parser.parse_known_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified — refuse and ask, never guess.")
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not results:
                print("No output data to write.")
                return
            writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend', 'MoM Growth', 'Formula'])
            writer.writeheader()
            writer.writerows(results)
        print(f"Results written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

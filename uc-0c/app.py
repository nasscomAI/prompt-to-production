import argparse
import csv
import sys
import datetime

def load_dataset(filepath):
    """
    Reads the CSV dataset, validates columns, reports null count and which rows have nulls before returning.
    """
    expected_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames if reader.fieldnames else [])
            if not expected_columns.issubset(headers):
                print(f"Error: Missing expected columns. Found: {headers}", file=sys.stderr)
                sys.exit(1)
            
            for row_idx, row in enumerate(reader, start=2):
                data.append(row)
                if not row['actual_spend'].strip():
                    null_rows.append({
                        'row_num': row_idx,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row['notes']
                    })
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    
    return data, len(null_rows), null_rows

def compute_growth(data, ward, category, growth_type):
    """
    Computes period-over-period growth for a specific ward and category.
    Includes the formula used in the output table.
    """
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a growth type (e.g., 'MoM').", file=sys.stderr)
        sys.exit(1)
        
    if not ward or not category or ward.lower() == 'all' or category.lower() == 'all':
        print("Error: You must specify a specific ward and category. Aggregation across wards or categories is strictly prohibited.", file=sys.stderr)
        sys.exit(1)

    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period to ensure chronic order
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        res = {
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual if actual else "NULL",
            'growth': "",
            'formula': ""
        }
        
        if not actual:
            res['growth'] = "Must be flagged — not computed"
            res['formula'] = f"Null value present. Reason: {notes}"
            results.append(res)
            continue
            
        current_val = float(actual)
        
        try:
            current_date = datetime.datetime.strptime(period, "%Y-%m")
        except ValueError:
            res['growth'] = "Error"
            res['formula'] = "Invalid period format"
            results.append(res)
            continue
            
        if growth_type.upper() == "MOM":
            month = current_date.month - 1
            year = current_date.year
            if month == 0:
                month = 12
                year -= 1
            prev_period = f"{year}-{month:02d}"
        elif growth_type.upper() == "YOY":
            prev_period = f"{current_date.year - 1}-{current_date.month:02d}"
        else:
            print(f"Error: Unsupported growth type '{growth_type}'.", file=sys.stderr)
            sys.exit(1)
            
        prev_row = next((r for r in filtered if r['period'] == prev_period), None)
        
        if prev_row:
            prev_actual = prev_row['actual_spend'].strip()
            if not prev_actual:
                res['growth'] = "N/A"
                res['formula'] = "Previous period value is null"
            else:
                prev_val = float(prev_actual)
                if prev_val == 0:
                    res['growth'] = "N/A"
                    res['formula'] = f"({current_val} - 0) / 0"
                else:
                    growth = ((current_val - prev_val) / prev_val) * 100
                    sign_char = "+" if growth > 0 else "−" if growth < 0 else ""
                    res['growth'] = f"{sign_char}{abs(growth):.1f}%"
                    res['formula'] = f"({current_val} - {prev_val}) / {prev_val} * 100"
        else:
            res['growth'] = "N/A"
            res['formula'] = "No previous period data available"
            
        results.append(res)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate budget growth metrics.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=False, help="Specific ward to compute for")
    parser.add_argument("--category", required=False, help="Specific category to compute for")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a growth type (e.g., 'MoM').", file=sys.stderr)
        sys.exit(1)
        
    if not args.ward or not args.category or args.ward.strip().lower() == 'all' or args.category.strip().lower() == 'all':
        print("Error: You must specify a specific ward and category. Aggregation across wards or categories is strictly prohibited.", file=sys.stderr)
        sys.exit(1)
        
    data, null_count, null_rows = load_dataset(args.input)
    
    print(f"Loaded dataset. Found {null_count} null rows in actual_spend.")
    for nr in null_rows:
        print(f"  Flagged Null: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        # Dynamically named growth column
        fieldnames = ['ward', 'category', 'period', 'actual_spend', f'{args.growth_type} Growth', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in results:
            out_row = {
                'ward': row['ward'],
                'category': row['category'],
                'period': row['period'],
                'actual_spend': row['actual_spend'],
                f'{args.growth_type} Growth': row['growth'],
                'formula': row['formula']
            }
            writer.writerow(out_row)
            
    print(f"Successfully computed requested growth and wrote to {args.output}")

if __name__ == "__main__":
    main()


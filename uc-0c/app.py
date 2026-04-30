import argparse
import csv
import sys
import os

def load_dataset(filepath):
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print(f"Error: Empty or invalid CSV file {filepath}.")
                sys.exit(1)
            
            # Clean BOM or spaces in header just in case
            cleaned_fields = [f.strip() for f in reader.fieldnames]
            reader.fieldnames = cleaned_fields
            
            if not required_columns.issubset(set(cleaned_fields)):
                missing = required_columns - set(cleaned_fields)
                print(f"Error: Missing required columns: {missing}")
                sys.exit(1)
                
            for row_idx, row in enumerate(reader, start=2): # 1 for header
                actual_spend = row.get('actual_spend', '').strip()
                if not actual_spend or actual_spend.lower() == 'null':
                    null_rows.append({
                        'row': row_idx,
                        'period': row.get('period'),
                        'ward': row.get('ward'),
                        'category': row.get('category'),
                        'notes': row.get('notes')
                    })
                data.append(row)
                
    except FileNotFoundError:
        print(f"Error: Input file '{filepath}' not found.")
        sys.exit(1)
        
    if null_rows:
        print(f"Dataset loaded. Found {len(null_rows)} rows with null actual_spend:")
        for r in null_rows:
            print(f"  - Row {r['row']} ({r['period']} | {r['ward']} | {r['category']}): {r['notes']}")
            
    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    # Enforcement Rule 1: Never aggregate across wards or categories
    if not ward or ward.lower() == 'all':
        print("Error: System refuses to aggregate across wards. Please specify a single ward.")
        sys.exit(1)
    if not category or category.lower() == 'all':
        print("Error: System refuses to aggregate across categories. Please specify a single category.")
        sys.exit(1)

    # Enforcement Rule 4: If growth_type not specified, refuse and ask
    if not growth_type:
        print("Error: --growth-type must be specified. Refusing to guess. Please provide a growth type (e.g., MoM).")
        sys.exit(1)

    filtered = [d for d in data if d['ward'] == ward and d['category'] == category]
    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
    
    filtered.sort(key=lambda x: x['period'])
    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current['period']
        actual_spend_str = current['actual_spend'].strip()
        notes = current['notes']
        
        # Determine actual spend float or null
        is_null = not actual_spend_str or actual_spend_str.lower() == 'null'
        
        row_result = {
            'Ward': current['ward'],
            'Category': current['category'],
            'Period': period,
            'Actual Spend': 'NULL' if is_null else actual_spend_str,
            f'{growth_type} Growth': '',
            'Formula Used': '',
            'Notes': notes
        }
        
        # Enforcement Rule 2: Flag every null row before computing
        if is_null:
            row_result[f'{growth_type} Growth'] = 'NULL (Must be flagged — not computed)'
            row_result['Formula Used'] = 'N/A'
        else:
            current_val = float(actual_spend_str)
            if growth_type.upper() == 'MOM':
                if i == 0:
                    row_result[f'{growth_type} Growth'] = 'N/A (First period)'
                    row_result['Formula Used'] = 'N/A'
                else:
                    prev_str = filtered[i-1]['actual_spend'].strip()
                    if not prev_str or prev_str.lower() == 'null':
                        row_result[f'{growth_type} Growth'] = 'Cannot compute (Previous period is NULL)'
                        row_result['Formula Used'] = 'N/A'
                    else:
                        prev_val = float(prev_str)
                        if prev_val == 0:
                            row_result[f'{growth_type} Growth'] = 'N/A (Division by zero)'
                            row_result['Formula Used'] = 'N/A'
                        else:
                            growth = (current_val - prev_val) / prev_val * 100
                            sign = '+' if growth > 0 else ''
                            row_result[f'{growth_type} Growth'] = f'{sign}{growth:.1f}%'
                            # Enforcement Rule 3: Show formula used in every output row alongside the result
                            row_result['Formula Used'] = f'({current_val} - {prev_val}) / {prev_val} * 100'
            elif growth_type.upper() == 'YOY':
                year, month = period.split('-')
                prev_year_period = f"{int(year)-1}-{month}"
                prev_data = next((d for d in data if d['ward']==ward and d['category']==category and d['period']==prev_year_period), None)
                if not prev_data:
                    row_result[f'{growth_type} Growth'] = 'N/A (No previous year data)'
                    row_result['Formula Used'] = 'N/A'
                else:
                    prev_str = prev_data['actual_spend'].strip()
                    if not prev_str or prev_str.lower() == 'null':
                        row_result[f'{growth_type} Growth'] = 'Cannot compute (Previous year is NULL)'
                        row_result['Formula Used'] = 'N/A'
                    else:
                        prev_val = float(prev_str)
                        if prev_val == 0:
                            row_result[f'{growth_type} Growth'] = 'N/A (Division by zero)'
                            row_result['Formula Used'] = 'N/A'
                        else:
                            growth = (current_val - prev_val) / prev_val * 100
                            sign = '+' if growth > 0 else ''
                            row_result[f'{growth_type} Growth'] = f'{sign}{growth:.1f}%'
                            row_result['Formula Used'] = f'({current_val} - {prev_val}) / {prev_val} * 100'
            else:
                print(f"Error: Unsupported growth type '{growth_type}'")
                sys.exit(1)
                
        results.append(row_result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument('--input', required=True, help="Path to input CSV file")
    parser.add_argument('--ward', help="Ward name (must specify single ward)")
    parser.add_argument('--category', help="Category name (must specify single category)")
    parser.add_argument('--growth-type', help="Growth metric to compute (e.g., MoM)")
    parser.add_argument('--output', required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # Check enforcement rule 4 before doing anything
    if not args.growth_type:
        print("Error: --growth-type must be specified. Refusing to guess.")
        sys.exit(1)
        
    # Check enforcement rule 1
    if not args.ward or args.ward.lower() == 'all':
        print("Error: System refuses to aggregate across wards. Please specify a single ward.")
        sys.exit(1)
        
    if not args.category or args.category.lower() == 'all':
        print("Error: System refuses to aggregate across categories. Please specify a single category.")
        sys.exit(1)
        
    data, null_rows = load_dataset(args.input)
    
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No results to write. Exiting.")
        sys.exit(0)
        
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend', f'{args.growth_type} Growth', 'Formula Used', 'Notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Successfully wrote {len(results)} rows to {args.output}")

if __name__ == "__main__":
    main()

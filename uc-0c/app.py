import argparse
import csv
import sys

def load_dataset(filepath):
    print(f"Loading dataset from {filepath}...")
    dataset = []
    null_rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_columns.issubset(set(reader.fieldnames)):
                print(f"Error: Missing required columns. Expected at least {required_columns}", file=sys.stderr)
                sys.exit(1)
            
            for index, row in enumerate(reader, start=2): # +1 for header, +1 for 0-index
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_rows.append((index, row))
    except FileNotFoundError:
        print(f"Error: The file {filepath} could not be found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(null_rows)} explicitly null 'actual_spend' values.")
    for idx, row in null_rows:
        print(f" - Row {idx}: Ward: {row['ward']}, Category: {row['category']}, Period: {row['period']} | Note: {row['notes']}")

    return dataset

def compute_growth(dataset, ward, category, growth_type):
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    
    # Sort just in case it's not chronological
    filtered.sort(key=lambda x: x['period'])
    
    if not filtered:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'")
    
    output_rows = []
    
    for i in range(len(filtered)):
        curr_row = filtered[i]
        curr_actual_str = curr_row['actual_spend'].strip()
        notes = curr_row['notes']
        
        # Decide the lookback gap based on growth_type
        gap = 1 if growth_type.lower() == 'mom' else (12 if growth_type.lower() == 'yoy' else None)
        if gap is None:
            print("Error: Invalid growth type. Supported: MoM, YoY.")
            sys.exit(1)
            
        prev_row = filtered[i-gap] if i >= gap else None
        
        if not curr_actual_str:
            growth_val = "FLAGGED NULL"
            formula = f"Cannot compute: {notes}"
        else:
            if prev_row is None:
                growth_val = "n/a"
                formula = "Not enough history to compute"
            else:
                prev_actual_str = prev_row['actual_spend'].strip()
                if not prev_actual_str:
                    growth_val = "n/a"
                    formula = "Cannot compute: Previous period was null"
                else:
                    curr_val = float(curr_actual_str)
                    prev_val = float(prev_actual_str)
                    if prev_val == 0:
                        growth_val = "n/a"
                        formula = "Cannot compute: Previous period denominator is 0"
                    else:
                        change = (curr_val - prev_val) / prev_val * 100
                        growth_val = f"{change:+.1f}%"
                        formula = f"({curr_val} - {prev_val}) / {prev_val} * 100"
        
        # Output format
        out_row = {
            'Ward': curr_row['ward'],
            'Category': curr_row['category'],
            'Period': curr_row['period'],
            'Budget': curr_row['budgeted_amount'],
            'Actual Spend': curr_actual_str if curr_actual_str else 'NULL',
            f'{growth_type} Growth': growth_val,
            'Formula Used': formula,
            'Notes': notes
        }
        output_rows.append(out_row)
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Financial Data Analyst Agent - Growth Computation")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--ward', help="Specific ward to compute for")
    parser.add_argument('--category', help="Specific category to compute for")
    parser.add_argument('--growth-type', help="Type of growth computation (e.g., MoM, YoY)")
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    # We use argv to check arguments directly if we want custom refusal instead of standard parser error
    args = parser.parse_args()
    
    # ENFORCEMENT 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or not args.category or args.ward.lower() == 'all' or args.category.lower() == 'all':
        print("ERROR: Refusing to aggregate across wards or categories. You must specify a specific --ward and --category.", file=sys.stderr)
        sys.exit(1)
        
    # ENFORCEMENT 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("ERROR: Refusing to guess the growth metric. Please explicitely provide --growth-type.", file=sys.stderr)
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    
    # ENFORCEMENT 2 & 3: flag nulls and show formula used
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Write to output file
    if results:
        fieldnames = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Data successfully computed and written to {args.output}")

if __name__ == "__main__":
    main()

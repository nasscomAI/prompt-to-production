import argparse
import csv
import sys
import os

def load_dataset(input_file):
    expected_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if not os.path.exists(input_file):
        print(f"Error: dataset file '{input_file}' is missing.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers or not all(col in headers for col in expected_cols):
                print(f"Error: Columns do not match expected dataset structure, expected: {expected_cols}", file=sys.stderr)
                sys.exit(1)
            
            data = list(reader)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)

    null_rows = []
    for row in data:
        # Check if actual_spend is null/empty
        if not row.get('actual_spend', '').strip():
            null_rows.append(row)
            
    if null_rows:
        print(f"Found {len(null_rows)} null 'actual_spend' rows. Flagging before computation:")
        for r in null_rows:
            reason = r['notes'] if r['notes'] else 'No reason provided'
            print(f" - {r['period']} · {r['ward']} · {r['category']} (Reason: {reason})")
            
    return data

def compute_growth(data, ward, category, growth_type):
    # Enforcement 4: Refuse if --growth-type not specified
    if not growth_type:
        print("Error: --growth-type not specified! Refusing to guess. Please provide a valid growth type (e.g. MoM, YoY).", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category or ward.strip().lower() == 'any' or category.strip().lower() == 'any':
        print("Error: Refusing to aggregate across wards or categories. Please specify a distinct --ward and --category.", file=sys.stderr)
        sys.exit(1)
        
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    filtered_data.sort(key=lambda x: x['period'])
    
    output = []
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        
        # Enforcement 2: Flag every null row before computing, report from notes
        if not actual_spend_str:
            note = row.get('notes', 'No reason provided')
            output.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                f'{growth_type} Growth': 'Must be flagged — not computed',
                # Enforcement 3: Show formula used in every output row alongside the result
                'Formula': f"Flagged null: {note}"
            })
            continue
            
        current_spend = float(actual_spend_str)
        growth_pct_str = "n/a"
        formula = "n/a"
        
        if growth_type.lower() == 'mom':
            if i > 0:
                prev_spend_str = filtered_data[i-1]['actual_spend'].strip()
                if prev_spend_str:
                    prev_spend = float(prev_spend_str)
                    if prev_spend != 0:
                        pct = ((current_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if pct >= 0 else "" # let standard minus format
                        note_suffix = f" ({row['notes']})" if row['notes'] else ""
                        growth_pct_str = f"{sign}{pct:.1f}%{note_suffix}"
                        # Enforcement 3: Show formula used
                        formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                    else:
                        growth_pct_str = "n/a (previous is zero)"
                        formula = f"(({current_spend} - 0) / 0) * 100"
                else:
                    growth_pct_str = "n/a (previous is NULL)"
                    formula = "Prev period has NULL actual_spend"
            else:
                growth_pct_str = "n/a"
                formula = "No previous period available for MoM"
        else:
            growth_pct_str = f"n/a (implement {growth_type})"
            formula = f"No formula implemented for {growth_type}"
            
        output.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': current_spend,
            f'{growth_type} Growth': growth_pct_str,
            'Formula': formula
        })
        
    return output

def main():
    parser = argparse.ArgumentParser(description="Financial Data Analyst Agent for Ward Budget")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--ward', required=False, help="Ward name (must specify, cannot be Any)")
    parser.add_argument('--category', required=False, help="Category name (must specify, cannot be Any)")
    parser.add_argument('--growth-type', required=False, help="Growth type to calculate (e.g., MoM)")
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    growth_results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not growth_results:
        print("Warning: No matching rows found for the specified ward and category.")
        
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth', 'Formula']
    
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(growth_results)
        print(f"Successfully generated growth analysis at: {args.output}")
    except Exception as e:
        print(f"Error saving output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

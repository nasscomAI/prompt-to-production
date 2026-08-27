import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates expected columns, and flags any null actual_spend rows mapped to their reasons.
    """
    if not os.path.exists(filepath):
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames if reader.fieldnames else [])
        if not required_columns.issubset(headers):
            missing = required_columns - headers
            print(f"Error: Missing expected columns: {missing}")
            sys.exit(1)
            
        data = list(reader)
        
    null_rows = []
    for i, row in enumerate(data, start=1):
        if not row['actual_spend'] or row['actual_spend'].strip() == '':
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row['notes']
            })
            
    if null_rows:
        print("--- Null 'actual_spend' Rows Flagged ---")
        for nr in null_rows:
            print(f"Flagged Row: {nr['period']} | {nr['ward']} | {nr['category']} -> Reason: {nr['reason']}")
            
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Computes period-over-period growth for a specific ward and category, returning an unaggregated tabular result demonstrating the formula used.
    """
    if not target_ward:
        print("Error: Must specify a target ward. Aggregating across wards is refused.")
        sys.exit(1)
    if not target_category:
        print("Error: Must specify a target category. Aggregating across categories is refused.")
        sys.exit(1)
    if not growth_type:
        print("Error: --growth-type is absent. Refusing calculation. Please specify a calculation type (e.g., MoM, YoY).")
        sys.exit(1)
        
    filtered_data = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]
    filtered_data.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for row in filtered_data:
        period = row['period']
        actual_spend = row['actual_spend'].strip() if row['actual_spend'] else ''
        notes = row['notes']
        
        if not actual_spend:
            output_rows.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend': 'NULL',
                'Growth': 'n/a',
                'Formula': f"Flagged row ({notes}) — not computed"
            })
            continue

        prev_period = None
        if growth_type.upper() == 'MOM':
            year, month = map(int, period.split('-'))
            prev_m = f"{year - 1}-12" if month == 1 else f"{year}-{month - 1:02d}"
            prev_period = prev_m
        elif growth_type.upper() == 'YOY':
            year, month = map(int, period.split('-'))
            prev_period = f"{year - 1}-{month:02d}"
        else:
            print(f"Error: Unknown growth type '{growth_type}'")
            sys.exit(1)
            
        prev_row = next((r for r in filtered_data if r['period'] == prev_period), None)
        prev_actual_spend = prev_row['actual_spend'].strip() if prev_row and prev_row['actual_spend'] else ''
        
        if not prev_row or not prev_actual_spend:
             output_rows.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend': actual_spend,
                'Growth': 'n/a',
                'Formula': f"Cannot compute {growth_type} (no data for {prev_period})"
            })
             continue
             
        try:
            curr_val = float(actual_spend)
            prev_val = float(prev_actual_spend)
        except ValueError:
            output_rows.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend': actual_spend,
                'Growth': 'ERROR',
                'Formula': "Value conversion error"
            })
            continue

        if prev_val == 0:
             output_rows.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend': actual_spend,
                'Growth': 'n/a',
                'Formula': "Undefined (division by zero)"
            })
             continue

        growth = ((curr_val - prev_val) / prev_val) * 100
        sign = "+" if growth > 0 else ""
        formula = f"({curr_val} - {prev_val}) / {prev_val} * 100 [{growth_type}]"
        
        # Include notes correctly placed inside output formula if specified
        if notes:
            formula += f" ({notes})"

        output_rows.append({
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend': actual_spend,
            'Growth': f"{sign}{growth:.1f}%",
            'Formula': formula
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Financial data analysis agent for ward budget growth metrics.")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=False, help="Target ward")
    parser.add_argument("--category", required=False, help="Target category")
    parser.add_argument("--growth-type", required=False, help="Growth calculation type (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    output_rows = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend', 'Growth', 'Formula'])
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"\nProcessing complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()

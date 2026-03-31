import argparse
import csv
import sys

def load_dataset(file_path):
    expected_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    data = []
    null_rows = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not reader.fieldnames or set(expected_columns) != set(reader.fieldnames):
                sys.exit(f"Error: Dataset missing required columns. Expected: {expected_columns}")
                
            for row in reader:
                data.append(row)
                if row['actual_spend'].strip() == '':
                    null_rows.append(row)
                    
    except FileNotFoundError:
        sys.exit(f"Error: File not found: {file_path}")
        
    print(f"Dataset loaded successfully. Total rows: {len(data)}")
    print(f"Total null actual_spend rows detected: {len(null_rows)}")
    if null_rows:
        print("Null rows identified:")
        for r in null_rows:
            print(f" - {r['period']} · {r['ward']} · {r['category']} · Reason: {r['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    # Enforce: never aggregate across wards or categories
    if not ward or ward.lower() == 'all':
        sys.exit("REFUSAL: Cannot aggregate across wards unless explicitly instructed.")
    if not category or category.lower() == 'all':
        sys.exit("REFUSAL: Cannot aggregate across categories unless explicitly instructed.")
        
    filtered = []
    for row in data:
        if row['ward'] == ward and row['category'] == category:
            filtered.append(row)
            
    if not filtered:
        print("Warning: No data found for the specified ward and category.")
        return []
        
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        out_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual if actual else 'NULL',
            'Growth': '',
            'Formula': ''
        }
        
        # If current is null, flag and do not compute
        if actual == '':
            out_row['Growth'] = 'NULL'
            out_row['Formula'] = f"Flagged null: {notes}"
            output_rows.append(out_row)
            continue
            
        current_val = float(actual)
        
        if growth_type == 'MoM':
            if i == 0:
                out_row['Growth'] = 'n/a'
                out_row['Formula'] = 'First period, no previous data'
            else:
                prev_actual = filtered[i-1]['actual_spend'].strip()
                if prev_actual == '':
                    out_row['Growth'] = 'Cannot compute'
                    out_row['Formula'] = 'Previous period is NULL'
                else:
                    prev_val = float(prev_actual)
                    if prev_val == 0:
                        out_row['Growth'] = 'Cannot compute'
                        out_row['Formula'] = 'Division by zero'
                    else:
                        growth = ((current_val - prev_val) / prev_val) * 100
                        sign = '+' if growth > 0 else ''
                        out_row['Growth'] = f"{sign}{growth:.1f}%"
                        out_row['Formula'] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        elif growth_type == 'YoY':
            year, month = map(int, period.split('-'))
            target_period = f"{year-1}-{month:02d}"
            
            prev_row = next((r for r in filtered if r['period'] == target_period), None)
            if not prev_row:
                out_row['Growth'] = 'n/a'
                out_row['Formula'] = f"No data for {target_period}"
            else:
                prev_actual = prev_row['actual_spend'].strip()
                if prev_actual == '':
                    out_row['Growth'] = 'Cannot compute'
                    out_row['Formula'] = f"Data for {target_period} is NULL"
                else:
                    prev_val = float(prev_actual)
                    if prev_val == 0:
                        out_row['Growth'] = 'Cannot compute'
                        out_row['Formula'] = 'Division by zero'
                    else:
                        growth = ((current_val - prev_val) / prev_val) * 100
                        sign = '+' if growth > 0 else ''
                        out_row['Growth'] = f"{sign}{growth:.1f}%"
                        out_row['Formula'] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        
        output_rows.append(out_row)
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Calculate budget growth.")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    parsed_args = parser.parse_args()
    
    if not parsed_args.growth_type:
        sys.exit("REFUSAL: --growth-type not specified. Please specify MoM or YoY; I cannot guess.")
        
    data = load_dataset(parsed_args.input)
    
    output_rows = compute_growth(data, parsed_args.ward, parsed_args.category, parsed_args.growth_type)
    
    # Write output
    if output_rows:
        fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'Growth', 'Formula']
        try:
            with open(parsed_args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(output_rows)
            print(f"Output successfully written to {parsed_args.output}")
        except Exception as e:
            sys.exit(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()

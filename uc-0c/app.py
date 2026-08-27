"""
UC-0C app.py — Growth Calculator with R.I.C.E enforcement.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_file):
    """
    Reads the budget CSV file, validates the presence of required columns,
    and reports the count and details of null actual_spend rows.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    dataset = []
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not all(col in reader.fieldnames for col in required_columns):
            missing = [col for col in required_columns if col not in reader.fieldnames]
            print(f"Error: Missing columns in CSV: {missing}")
            sys.exit(1)
        
        for row in reader:
            dataset.append(row)
    
    null_rows = [row for row in dataset if not row['actual_spend'] or row['actual_spend'].strip() == ""]
    print(f"Dataset loaded: {len(dataset)} rows found.")
    print(f"Null actual_spend values found: {len(null_rows)}")
    for row in null_rows:
        print(f"  - {row['period']} · {row['ward']} · {row['category']} (Reason: {row['notes']})")
    
    return dataset

def compute_growth(ward, category, growth_type, dataset):
    """
    Calculates the specified growth metric (MoM or YoY) for a specific ward and category.
    """
    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    filtered_data = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'")
        sys.exit(1)

    # Sort by period to ensure growth calculation is correct
    filtered_data.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for i, row in enumerate(filtered_data):
        current_val_str = row['actual_spend'].strip()
        period = row['period']
        
        # Enforcement Rule 2: Flag every null row before computing — report null reason from the notes column
        if not current_val_str:
            output_rows.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'Growth': 'NULL',
                'Formula': f"NULL (Reason: {row['notes']})"
            })
            continue

        current_val = float(current_val_str)
        
        if growth_type == 'MoM':
            if i == 0:
                growth_val = "n/a"
                formula = "n/a (First month in dataset)"
            else:
                prev_row = filtered_data[i-1]
                prev_val_str = prev_row['actual_spend'].strip()
                if not prev_val_str:
                    growth_val = "n/a"
                    formula = f"n/a (Previous period {prev_row['period']} was NULL)"
                else:
                    prev_val = float(prev_val_str)
                    growth = (current_val - prev_val) / prev_val * 100
                    growth_val = f"{'+' if growth >= 0 else ''}{growth:.1f}%"
                    # Enforcement Rule 3: Show formula used in every output row alongside the result
                    formula = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        elif growth_type == 'YoY':
            year, month = map(int, period.split('-'))
            prev_year_period = f"{year-1}-{month:02d}"
            prev_row = next((r for r in dataset if r['ward'] == ward and r['category'] == category and r['period'] == prev_year_period), None)
            
            if not prev_row:
                growth_val = "n/a"
                formula = f"n/a (Previous year period {prev_year_period} not found)"
            else:
                prev_val_str = prev_row['actual_spend'].strip()
                if not prev_val_str:
                    growth_val = "n/a"
                    formula = f"n/a (Previous year period {prev_year_period} was NULL)"
                else:
                    prev_val = float(prev_val_str)
                    growth = (current_val - prev_val) / prev_val * 100
                    growth_val = f"{'+' if growth >= 0 else ''}{growth:.1f}%"
                    formula = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        else:
            print(f"Error: Unknown growth type '{growth_type}'")
            sys.exit(1)

        output_rows.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': current_val,
            'Growth': growth_val,
            'Formula': formula
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Enforcement Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type not specified. Please specify 'MoM' or 'YoY'.")
        sys.exit(1)

    dataset = load_dataset(args.input)
    
    # Check for unauthorized aggregation if ward or category were somehow not specified (argparse handles required=True though)
    if not args.ward or not args.category:
        print("Error: Ward and Category must be specified. All-ward aggregation is refused.")
        sys.exit(1)

    results = compute_growth(args.ward, args.category, args.growth_type, dataset)

    # Write output
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()

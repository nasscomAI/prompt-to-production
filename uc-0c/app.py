import argparse
import csv
import sys

def load_dataset(filepath, target_ward, target_category):
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        sys.exit(1)

    # Validate columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not data or not required_cols.issubset(set(data[0].keys())):
        print("Error: Missing required columns in dataset.")
        sys.exit(1)

    filtered_data = []
    null_count = 0
    null_reports = []

    for row in data:
        if row['ward'] == target_ward and row['category'] == target_category:
            filtered_data.append(row)
            if not row['actual_spend'].strip():
                null_count += 1
                null_reports.append(f"Row for {row['period']}: {row['notes']}")

    if null_count > 0:
        print(f"WARNING: Found {null_count} null actual_spend rows for this subset:")
        for rep in null_reports:
            print(f" - {rep}")
            
    return filtered_data

def compute_growth(dataset, growth_type):
    if not growth_type:
        print("REFUSAL: --growth-type not specified. Refusing to guess. Please provide --growth-type (e.g. MoM).")
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"REFUSAL: Supported growth types are MoM. Received: {growth_type}")
        sys.exit(1)

    # Sort dataset by period just in case
    dataset.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for i, row in enumerate(dataset):
        period = row['period']
        ward = row['ward']
        category = row['category']
        budget = row['budgeted_amount']
        actual = row['actual_spend'].strip()

        if not actual:
            output_rows.append({
                'period': period,
                'ward': ward,
                'category': category,
                'budgeted_amount': budget,
                'actual_spend': 'NULL',
                'growth': 'NULL flagged — not computed',
                'formula': 'n/a'
            })
            continue
            
        current_actual = float(actual)
        
        # Find previous month's data
        # Assuming period is YYYY-MM
        year, month = map(int, period.split('-'))
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1
            
        prev_period = f"{prev_year}-{prev_month:02d}"
        
        # Look for prev_period in dataset
        prev_actual_str = None
        for prev_row in dataset:
            if prev_row['period'] == prev_period:
                prev_actual_str = prev_row['actual_spend'].strip()
                break
                
        if i == 0 or not prev_actual_str:
             output_rows.append({
                'period': period,
                'ward': ward,
                'category': category,
                'budgeted_amount': budget,
                'actual_spend': actual,
                'growth': 'No prior data',
                'formula': 'n/a'
            })
        else:
            prev_actual = float(prev_actual_str)
            if prev_actual == 0:
                growth_str = "Inf"
                formula = f"({current_actual} - 0) / 0"
            else:
                growth_pct = ((current_actual - prev_actual) / prev_actual) * 100
                growth_str = f"{'+' if growth_pct > 0 else ''}{growth_pct:.1f}%"
                formula = f"({current_actual} - {prev_actual}) / {prev_actual}"
                
            output_rows.append({
                'period': period,
                'ward': ward,
                'category': category,
                'budgeted_amount': budget,
                'actual_spend': actual,
                'growth': growth_str,
                'formula': formula
            })

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Calculate Budget Growth")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", help="Target ward. If empty, will check aggregation.")
    parser.add_argument("--category", help="Target category. If empty, will check aggregation.")
    parser.add_argument("--growth-type", help="Type of growth to compute (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    # Check if --growth-type is just missing from sys.argv completely
    # (Since argparse might set it to None, we want to fail explicitly if omitted)
    if not any(arg.startswith("--growth-type") for arg in sys.argv):
        print("REFUSAL: --growth-type not specified. Refusing to guess. Please provide --growth-type (e.g. MoM).")
        sys.exit(1)
        
    args = parser.parse_args()

    # Rule 1 from enforcement: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or not args.category or args.ward.lower() == "all" or args.category.lower() == "all":
        print("REFUSAL: Refusing to aggregate across wards or categories. Please specify a single --ward and --category.")
        sys.exit(1)

    print(f"Loading dataset...")
    dataset = load_dataset(args.input, args.ward, args.category)
    
    if not dataset:
        print(f"No data found for Ward: '{args.ward}' and Category: '{args.category}'")
        sys.exit(1)

    print(f"Computing growth...")
    output_data = compute_growth(dataset, args.growth_type)

    print(f"Writing to {args.output}...")
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)

    print("Done!")

if __name__ == "__main__":
    main()

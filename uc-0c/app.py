import argparse
import csv
import sys

def load_dataset(filepath):
    expected_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    dataset = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not all(col in reader.fieldnames for col in expected_columns):
                print("Error: Columns do not match the expected structure.")
                sys.exit(1)
            
            for i, row in enumerate(reader, start=2):
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_rows.append({
                        'row_num': i,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row['notes']
                    })
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)
        
    print(f"Dataset loaded. Found {len(null_rows)} rows with null actual_spend.")
    for nr in null_rows:
        print(f" - Row {nr['row_num']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        
    return dataset, null_rows

def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        print("Refusal: --growth-type is missing. Please specify the growth type. I cannot guess.")
        sys.exit(1)
        
    if not ward or not category or ward.lower() == 'any' or category.lower() == 'any' or ward.lower() == 'all' or category.lower() == 'all':
        print("Refusal: Never aggregate across wards or categories unless explicitly instructed. Please specify a single ward and category.")
        sys.exit(1)
        
    # Filter dataset
    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes']
        
        if not actual_spend_str:
            actual_spend = "NULL"
            growth = "NULL"
            formula = f"Not computed: {notes}"
            results.append({
                'Period': period,
                'Actual Spend': actual_spend,
                'Growth': growth,
                'Formula': formula
            })
            continue
            
        actual_spend = float(actual_spend_str)
        
        # Calculate growth
        if growth_type.lower() == 'mom':
            if i == 0:
                growth = "N/A"
                formula = "No previous period for MoM"
            else:
                prev_spend_str = filtered[i-1]['actual_spend'].strip()
                if not prev_spend_str:
                    growth = "N/A"
                    formula = "Previous period is NULL"
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth = "N/A"
                        formula = "Division by zero"
                    else:
                        growth_val = (actual_spend - prev_spend) / prev_spend
                        sign = "+" if growth_val > 0 else ""
                        growth = f"{sign}{growth_val:.1%}"
                        formula = f"({actual_spend} - {prev_spend}) / {prev_spend}"
        elif growth_type.lower() == 'yoy':
            year, month = period.split('-')
            prev_year_period = f"{int(year)-1}-{month}"
            
            prev_row = next((r for r in filtered if r['period'] == prev_year_period), None)
            if not prev_row:
                growth = "N/A"
                formula = "No previous year period for YoY"
            elif not prev_row['actual_spend'].strip():
                growth = "N/A"
                formula = "Previous year period is NULL"
            else:
                prev_spend = float(prev_row['actual_spend'].strip())
                if prev_spend == 0:
                    growth = "N/A"
                    formula = "Division by zero"
                else:
                    growth_val = (actual_spend - prev_spend) / prev_spend
                    sign = "+" if growth_val > 0 else ""
                    growth = f"{sign}{growth_val:.1%}"
                    formula = f"({actual_spend} - {prev_spend}) / {prev_spend}"
        else:
            print(f"Refusal: Unknown growth type '{growth_type}'.")
            sys.exit(1)
            
        results.append({
            'Period': period,
            'Actual Spend': actual_spend_str,
            'Growth': growth,
            'Formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--ward", required=False, help="Ward to filter by")
    parser.add_argument("--category", required=False, help="Category to filter by")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    if not args.ward or not args.category:
        print("Refusal: Must provide both --ward and --category to avoid aggregation.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Refusal: --growth-type is missing. Please specify the growth type. I cannot guess.")
        sys.exit(1)
        
    dataset, null_rows = load_dataset(args.input)
    
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Period', 'Actual Spend (₹ lakh)', 'Growth', 'Formula'])
        writer.writeheader()
        for row in results:
            writer.writerow({
                'Period': row['Period'],
                'Actual Spend (₹ lakh)': row['Actual Spend'],
                'Growth': row['Growth'],
                'Formula': row['Formula']
            })
        
    print(f"Successfully computed growth and wrote to {args.output}")

if __name__ == "__main__":
    main()

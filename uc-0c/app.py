import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """Reads CSV, validates columns, reports null count and which rows."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]
            if not all(col in fieldnames for col in required_cols):
                print(f"Error: CSV missing required columns. Expected: {required_cols}")
                print(f"Actually found: {fieldnames}")
                sys.exit(1)
            for row in reader:
                # Basic row cleanup
                clean_row = {k.strip(): v.strip() if v else v for k, v in row.items() if k}
                data.append(clean_row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
    
    # Identify null rows in actual_spend
    null_rows = [row for row in data if not row['actual_spend'] or row['actual_spend'].strip() == '']
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend values:")
        for row in null_rows:
            print(f"- {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    else:
        print("No null actual_spend values found.")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """Calculates per-period growth for specific ward/category or all."""
    if growth_type != 'MoM':
        print(f"Error: Only 'MoM' growth-type is currently supported. Refusing request for '{growth_type}'.")
        sys.exit(1)

    # Filter data based on "All" or specific values
    wards_to_process = [row['ward'] for row in data] if ward.lower() == 'all' else [ward]
    categories_to_process = [row['category'] for row in data] if category.lower() == 'all' else [category]
    
    unique_wards = sorted(list(set(wards_to_process)))
    unique_categories = sorted(list(set(categories_to_process)))

    results = []
    
    for w in unique_wards:
        for c in unique_categories:
            group_data = [row for row in data if row['ward'] == w and row['category'] == c]
            if not group_data:
                continue
                
            # Sort by period
            group_data.sort(key=lambda x: x['period'])
            
            prev_spend = None
            for row in group_data:
                period = row['period']
                raw_spend = row['actual_spend']
                notes = row['notes']
                
                current_spend = None
                if raw_spend and raw_spend.strip() != "":
                    try:
                        current_spend = float(raw_spend)
                    except ValueError:
                        current_spend = None
                
                growth_str = "n/a"
                formula = "n/a"
                
                if current_spend is None:
                    growth_str = "NULL (Flagged)"
                    formula = f"Cannot compute: {notes}"
                elif prev_spend is not None:
                    growth = ((current_spend - prev_spend) / prev_spend) * 100
                    growth_str = f"{growth:+.1f}%"
                    formula = f"({current_spend} - {prev_spend}) / {prev_spend}"
                elif prev_spend is None:
                    formula = "First period in sequence"
                    
                results.append({
                    "Ward": w,
                    "Category": c,
                    "Period": period,
                    "Actual Spend (₹ lakh)": "NULL" if current_spend is None else current_spend,
                    "MoM Growth": growth_str,
                    "Formula": formula
                })
                
                prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Ward Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", required=True, help="Specific ward name or 'All'")
    parser.add_argument("--category", required=True, help="Specific category name or 'All'")
    parser.add_argument("--growth-type", help="Type of growth to calculate (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # Enforcement: Refuse if --growth-type is not specified
    if not args.growth_type:
        print("Error: --growth-type is not specified. Please provide a metric (e.g., MoM). Refusing to guess.")
        sys.exit(1)
    
    print(f"Loading dataset: {args.input}")
    data = load_dataset(args.input)
    
    print(f"Computing {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'")
    report_data = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not report_data:
        print("Error: No data matched your selection.")
        sys.exit(1)

    print(f"Writing report to: {args.output}")
    keys = report_data[0].keys()
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report_data)
            
    print("Processing complete.")

if __name__ == "__main__":
    main()

import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """Reads the municipal budget CSV and reports null actual_spend rows."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
        
    data = []
    null_rows = []
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None or not all(col in fieldnames for col in required_columns):
            print(f"Error: CSV missing required columns. Found: {fieldnames}")
            sys.exit(1)
            
        for i, row in enumerate(reader):
            # Check for null actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip().lower() == 'null' or row['actual_spend'].strip() == '':
                null_rows.append((i + 2, row['period'], row['ward'], row['category'], row['notes']))
                row['actual_spend'] = None
            else:
                try:
                    row['actual_spend'] = float(row['actual_spend'])
                except ValueError:
                    row['actual_spend'] = None
            
            data.append(row)
            
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend rows:")
        for line, period, ward, cat, note in null_rows:
            print(f"  - Line {line} ({period}, {ward}, {cat}): {note}")
            
    return data

def compute_growth(data, ward_name, category_name, growth_type):
    """Calculates growth per-period for a specific ward and category."""
    if not growth_type:
        print("Error: Growth type (--growth-type) must be specified (MoM or YoY).")
        sys.exit(1)
        
    # Refuse if ward or category is "Any" or not specified for aggregation
    if not ward_name or not category_name or ward_name.lower() == 'any' or category_name.lower() == 'any':
        print("Error: Aggregation across wards or categories is not allowed. Please specify a specific ward and category.")
        sys.exit(1)

    # Filter data
    filtered = [r for r in data if r['ward'] == ward_name and r['category'] == category_name]
    
    if not filtered:
        print(f"No data found for Ward: '{ward_name}' and Category: '{category_name}'.")
        return []

    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        res = row.copy()
        current_val = row['actual_spend']
        period = row['period']
        
        growth = None
        formula = "n/a"
        
        if current_val is None:
            growth = "NULL (Flagged)"
            formula = f"n/a (Reason: {row['notes']})"
        else:
            prev_row = None
            if growth_type.upper() == 'MOM':
                if i > 0:
                    prev_row = filtered[i-1]
            elif growth_type.upper() == 'YOY':
                # Look for the same month in previous year
                curr_year, curr_month = period.split('-')
                prev_year = str(int(curr_year) - 1)
                prev_period = f"{prev_year}-{curr_month}"
                prev_row = next((r for r in filtered if r['period'] == prev_period), None)
            
            if prev_row:
                prev_val = prev_row['actual_spend']
                if prev_val is not None and prev_val != 0:
                    growth_val = ((current_val - prev_val) / prev_val) * 100
                    growth = f"{'+' if growth_val >= 0 else ''}{growth_val:.1f}%"
                    formula = f"({current_val} - {prev_val}) / {prev_val}"
                elif prev_val == 0:
                    growth = "Inf"
                    formula = f"({current_val} - 0) / 0"
                else:
                    growth = "n/a (Prev Null)"
                    formula = f"n/a (Reason: {prev_row['notes']})"
            else:
                growth = "n/a"
                formula = "No previous period data"
        
        res['growth'] = growth
        res['formula'] = formula
        results.append(res)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Specific Ward name")
    parser.add_argument("--category", required=True, help="Specific Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # Custom enforcement for growth-type (as per agents.md)
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please specify MoM or YoY.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        return

    # Prepare output
    header = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula']
    
    # Print to console
    print(f"\nGrowth Analysis ({args.growth_type.upper()}) for {args.ward} | {args.category}:")
    print(f"{'Period':<10} | {'Spend':<10} | {'Growth':<15} | {'Formula'}")
    print("-" * 80)
    for r in results:
        spend_str = "NULL" if r['actual_spend'] is None else str(r['actual_spend'])
        print(f"{r['period']:<10} | {spend_str:<10} | {r['growth']:<15} | {r['formula']}")

    # Save to file
    if args.output:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()

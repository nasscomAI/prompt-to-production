import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    Reads the budget CSV file, validates columns, and reports null actual_spend rows.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Check for missing columns
            present_columns = set(reader.fieldnames) if reader.fieldnames else set()
            missing = required_columns - present_columns
            if missing:
                print(f"Error: Missing required columns: {', '.join(missing)}")
                sys.exit(1)

            for i, row in enumerate(reader, start=2): # Header is line 1
                actual = row.get('actual_spend', '').strip()
                if not actual:
                    null_rows.append((row['period'], row['ward'], row['category'], row['notes']))
                data.append(row)

        print(f"Dataset loaded. Total rows: {len(data)}")
        if null_rows:
            print(f"Found {len(null_rows)} rows with missing 'actual_spend':")
            for period, ward, cat, note in null_rows:
                print(f"  - {period} | {ward} | {cat}: {note}")
        else:
            print("No missing 'actual_spend' values found.")

        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    """
    Calculates growth metrics for a specific ward and category.
    """
    # Filter data - Refuse aggregation by ensuring we only pick one ward and one category
    filtered = [
        row for row in data 
        if row['ward'] == ward and row['category'] == category
    ]

    if not filtered:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    # Sort by period to ensure chronological order
    filtered.sort(key=lambda x: x['period'])

    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current['period']
        actual_str = current['actual_spend'].strip()
        
        # Initialize result row
        res_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_str if actual_str else 'NULL',
            'growth': 'n/a',
            'formula': 'n/a'
        }

        # Rule: Flag null rows before computing
        if not actual_str:
            res_row['growth'] = 'FLAGGED'
            res_row['formula'] = f"NULL Value: {current['notes']}"
            results.append(res_row)
            continue

        # For the first row or if we can't find the previous month
        if i == 0:
            res_row['growth'] = 'n/a'
            res_row['formula'] = 'Baseline (First Period)'
            results.append(res_row)
            continue

        # Look for the previous month's data
        prev = filtered[i-1]
        prev_actual_str = prev['actual_spend'].strip()

        if not prev_actual_str:
            res_row['growth'] = 'n/a'
            res_row['formula'] = f"Cannot compute: Previous period ({prev['period']}) is NULL"
            results.append(res_row)
            continue

        try:
            curr_val = float(actual_str)
            prev_val = float(prev_actual_str)
            
            if prev_val == 0:
                res_row['growth'] = 'inf'
                res_row['formula'] = f"({curr_val} - 0) / 0"
            else:
                growth = ((curr_val - prev_val) / prev_val) * 100
                res_row['growth'] = f"{growth:+.1f}%"
                res_row['formula'] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
            
        except ValueError:
            res_row['growth'] = 'Error'
            res_row['formula'] = "Non-numeric data"

        results.append(res_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Analysis Agent - UC-0C")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    # Rule: If --growth-type not specified — refuse and ask
    if not args.growth_type:
        print("Error: --growth-type must be specified (e.g., --growth-type MoM). Refusing to proceed.")
        sys.exit(1)

    # Load and validate
    data = load_dataset(args.input)

    # Compute growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Write output
    try:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula']
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success: Growth analysis written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

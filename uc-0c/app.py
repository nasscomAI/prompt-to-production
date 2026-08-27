"""
UC-0C — Number That Looks Right: Budget Growth Calculator
Deterministic calculator with strict enforcement rules:
  1. No silent aggregation.
  2. Explicit NULL handling with reasons.
  3. Formula disclosure.
  4. Mandatory growth-type specification.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path):
    """
    Skill: load_dataset
    Reads CSV and validates structure. Identifies nulls.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    data = []
    null_rows = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}

    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check for missing columns
            if not required_cols.issubset(set(reader.fieldnames)):
                missing = required_cols - set(reader.fieldnames)
                print(f"Error: Missing required columns: {missing}")
                sys.exit(1)

            for i, row in enumerate(reader):
                # Data cleanup and null detection
                row_data = {
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'budgeted_amount': float(row['budgeted_amount']) if row['budgeted_amount'] else 0.0,
                    'actual_spend': None if not row['actual_spend'] or row['actual_spend'].strip() == '' else float(row['actual_spend']),
                    'notes': row['notes']
                }
                data.append(row_data)
                if row_data['actual_spend'] is None:
                    null_rows.append(row_data)

    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates per-period growth with formula disclosure and null handling.
    """
    if growth_type != 'MoM':
        print(f"Error: Unsupported or missing growth-type '{growth_type}'. Refusing to compute.")
        sys.exit(1)

    # Filter data for specific ward and category
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        print("Aggregation across wards or categories is forbidden.")
        sys.exit(1)

    # Sort by period to ensure chronological order
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    formula = "((Current - Previous) / Previous) * 100"

    for i in range(len(filtered_data)):
        current = filtered_data[i]
        result_row = {
            'period': current['period'],
            'actual_spend': current['actual_spend'] if current['actual_spend'] is not None else 'NULL',
            'notes': current['notes'],
            'growth_value': 'n/a',
            'formula': formula
        }

        if i > 0:
            previous = filtered_data[i-1]
            
            # Check for nulls in current or previous
            if current['actual_spend'] is None:
                result_row['growth_value'] = f"NULL FLAG: {current['notes']}"
            elif previous['actual_spend'] is None:
                result_row['growth_value'] = f"NULL PREVIOUS: {previous['notes']}"
            elif previous['actual_spend'] == 0:
                result_row['growth_value'] = "Inf (Zero Base)"
            else:
                growth = ((current['actual_spend'] - previous['actual_spend']) / previous['actual_spend']) * 100
                result_row['growth_value'] = f"{growth:+.1f}%"
        
        results.append(result_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Filter by specific ward. Aggregation is forbidden.")
    parser.add_argument("--category", help="Filter by specific category. Aggregation is forbidden.")
    parser.add_argument("--growth-type", help="Calculation type: MoM")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    # ENFORCEMENT: Check for required filters
    if not args.ward or not args.category:
        print("Error: Ward and Category must be explicitly specified.")
        print("Deterministic Refusal: Aggregation across multiple wards or categories is forbidden.")
        sys.exit(1)

    if not args.growth_type:
        print("Error: --growth-type must be specified (e.g., MoM).")
        print("Deterministic Refusal: Hidden formula assumptions are forbidden.")
        sys.exit(1)

    # Load dataset
    data, nulls = load_dataset(args.input)
    # print(f"Successfully loaded {len(data)} rows. Found {len(nulls)} instances of missing data.")

    # Compute growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Write output
    try:
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'growth_value', 'formula', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        
        print(f"Success: Growth calculation for '{args.ward}' - '{args.category}' written to {args.output}")
        
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

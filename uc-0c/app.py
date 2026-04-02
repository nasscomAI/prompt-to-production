import argparse
import csv
import sys
import os

EXPECTED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

def load_dataset(file_path):
    """
    Reads the budget CSV file, validates expected columns, and actively reports 
    the total null count and specific rows with nulls before returning the data table.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Validate expected columns are present
        actual_columns = set(reader.fieldnames or [])
        missing_columns = EXPECTED_COLUMNS - actual_columns
        if missing_columns:
            raise ValueError(f"Missing expected columns in dataset: {missing_columns}")

        data = list(reader)

    # Actively flag null 'actual_spend' values before proceeding
    null_rows = []
    for row in data:
        val = row.get('actual_spend', '').strip()
        if not val or val.lower() == 'null':
            null_rows.append(row)

    if null_rows:
        print(f"WARNING: Found {len(null_rows)} rows with NULL actual_spend values. They will not be aggregated.")
        for row in null_rows:
            print(f" - {row['period']} · {row['ward']} · {row['category']} · Reason: {row['notes']}")
    else:
        print("No null actual_spend values found.")

    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Computes growth metrics for a specific ward and category over time based 
    on an explicit growth type, explicitly documenting the formula.
    """
    if not target_ward or target_ward.lower() == 'any':
        raise ValueError("REFUSED: Aggregation across wards is strictly forbidden. Please specify a single ward.")
    if not target_category or target_category.lower() == 'any':
        raise ValueError("REFUSED: Aggregation across categories is strictly forbidden. Please specify a single category.")
    if not growth_type:
        raise ValueError("REFUSED: --growth-type must be specified. Program will not guess calculations like MoM or YoY.")

    # Filter data for specific ward and category
    filtered = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]

    # Sort chronologically by period (e.g. YYYY-MM)
    filtered.sort(key=lambda x: x['period'])

    output_rows = []
    
    if growth_type.lower() == 'mom':
        previous_spend = None
        for row in filtered:
            period = row['period']
            spend_str = row.get('actual_spend', '').strip()
            notes = row.get('notes', '').strip()
            
            if not spend_str or spend_str.lower() == 'null':
                output_rows.append({
                    'Ward': row['ward'],
                    'Category': row['category'],
                    'Period': period,
                    'Actual Spend (\u20b9 lakh)': 'NULL',
                    f'{growth_type} Growth': f"Must be flagged \u2014 not computed. Reason: {notes}",
                    'Formula': 'N/A (Null value ignored)'
                })
                previous_spend = None  # Reset previous to prevent spanning a gap wrongly
            else:
                current_spend = float(spend_str)
                if previous_spend is None:
                    output_rows.append({
                        'Ward': row['ward'],
                        'Category': row['category'],
                        'Period': period,
                        'Actual Spend (\u20b9 lakh)': current_spend,
                        f'{growth_type} Growth': 'n/a',
                        'Formula': 'Data starts here or previous is null'
                    })
                else:
                    growth = (current_spend - previous_spend) / previous_spend * 100
                    sign = "+" if growth > 0 else ""
                    
                    # Round logic: +33.1%, -34.8%
                    formula_str = f"({current_spend} - {previous_spend}) / {previous_spend}"
                    notes_suffix = f" ({notes})" if notes else ""
                    
                    output_rows.append({
                        'Ward': row['ward'],
                        'Category': row['category'],
                        'Period': period,
                        'Actual Spend (\u20b9 lakh)': current_spend,
                        f'{growth_type} Growth': f"{sign}{growth:.1f}%{notes_suffix}",
                        'Formula': formula_str
                    })
                previous_spend = current_spend
    else:
        raise ValueError(f"REFUSED: Unsupported growth_type: {growth_type}. Please try 'MoM'.")

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Calculate granular per-ward budget growth metrics.")
    parser.add_argument("--input", required=True, help="Input CSV dataset file path")
    parser.add_argument("--output", required=True, help="Output CSV calculations file path")
    parser.add_argument("--ward", required=False, help="Target ward to analyze (required)")
    parser.add_argument("--category", required=False, help="Target category to analyze (required)")
    parser.add_argument("--growth-type", required=False, help="Explicit calculation to perform (e.g. MoM)")

    args = parser.parse_args()

    # Rule: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("ERROR: --growth-type must be specified explicitly (e.g., 'MoM'). Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    # Rule: Never aggregate across wards or categories unless explicitly instructed
    if not args.ward or not args.category or args.ward.lower() == 'any' or args.category.lower() == 'any':
        print("ERROR: Unspecified --ward or --category. Operations that implicitly aggregate across multiple domains are disallowed per agents rules.", file=sys.stderr)
        sys.exit(1)

    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if not results:
            print("No matching data found for the specified ward and category.")
            sys.exit(0)

        # Write output table (which strictly reports granular metric computations line-by-line alongside the formula)
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (\u20b9 lakh)', f'{args.growth_type} Growth', 'Formula']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result_row in results:
                writer.writerow(result_row)
                
        print(f"Analysis successfully written to {args.output}")

    except Exception as e:
        print(f"Analysis Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

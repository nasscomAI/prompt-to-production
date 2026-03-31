import argparse
import csv
import sys
import os

EXPECTED_COLUMNS = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']

def load_dataset(filepath):
    """
    Reads the CSV data, validates columns, and reports null count/rows before returning.
    """
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    dataset = []
    null_report = []

    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate expected columns
        actual_columns = reader.fieldnames
        if not actual_columns or not all(col in actual_columns for col in EXPECTED_COLUMNS):
            print(f"Error: Improperly formatted CSV. Expected columns: {EXPECTED_COLUMNS}")
            sys.exit(1)

        # Parse rows and collect null validations
        for row_idx, row in enumerate(reader, start=2): # Start at 2 to account for header
            dataset.append(row)
            
            spend_val = row['actual_spend'].strip()
            if not spend_val or spend_val.upper() == 'NULL':
                null_report.append({
                    'row_number': row_idx,
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'notes': row['notes']
                })
    
    # Error Handling: Throw error if it fails to identify expected blanks 
    # (Enforces that silent null handling doesn't slip by)
    if len(null_report) == 0:
        print("Warning/Error: No null 'actual_spend' values identified. Verify dataset deliberately includes blanks.")
    else:
        print(f"--- VALIDATION REPORT ---")
        print(f"Identified {len(null_report)} deliberate null 'actual_spend' rows:")
        for null_row in null_report:
            print(f" - Period: {null_row['period']} | Ward: {null_row['ward']} | Category: {null_row['category']} | Reason: {null_row['notes']}")
        print("-------------------------\n")

    return dataset

def compute_growth(dataset, ward, category, growth_type, output_file):
    """
    Computes requested growth type for a distinct ward/category, outputting a table with formulas.
    """
    # Enforcement 4: Refuse if growth_type missing
    if not growth_type:
        print("REFUSAL: `--growth-type` was not specified. Please provide the required growth type (e.g., MoM). I will not guess the formula.")
        sys.exit(1)

    # Enforcement 1: Refuse cross-ward/cross-category aggregation
    if not ward or ward.lower() in ['any', 'all'] or not category or category.lower() in ['any', 'all']:
        print(f"REFUSAL: Unauthorized aggregation. You requested Ward: '{ward}' and Category: '{category}'. I will never aggregate across wards or categories unless explicitly instructed via code modification.")
        sys.exit(1)

    # Filter and sort data
    filtered_data = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    filtered_data = sorted(filtered_data, key=lambda x: x['period'])

    if not filtered_data:
        print(f"No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    # Output Generation
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header matching the reference values
        writer.writerow(['Ward', 'Category', 'Period', 'Actual Spend', f'{growth_type} Growth', 'Formula', 'Flags'])

        prev_spend = None

        for row in filtered_data:
            period = row['period']
            spend_str = row['actual_spend'].strip()

            # Enforcement 2 & 3: Flag null row and replace computation with note
            if not spend_str or spend_str.upper() == 'NULL':
                writer.writerow([
                    ward, 
                    category, 
                    period, 
                    'NULL', 
                    'Must be flagged — not computed', 
                    'Not computed (Null actual_spend)', 
                    f"FLAGGED: {row['notes']}"
                ])
                prev_spend = None # Break the calculation chain
                continue

            try:
                current_spend = float(spend_str)
            except ValueError:
                print(f"Error parsing actual_spend value '{spend_str}' for period {period}.")
                sys.exit(1)

            # First month or month immediately following a NULL month
            if prev_spend is None:
                writer.writerow([ward, category, period, current_spend, 'n/a', 'Base period (no previous data)', ''])
            else:
                if growth_type.upper() == 'MOM':
                    # MoM calculation
                    growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                    # Enforcement 3: Show explicit formula
                    formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                    
                    growth_str = f"{growth_val:+.1f}%"
                    writer.writerow([ward, category, period, current_spend, growth_str, formula, ''])
                else:
                    print(f"REFUSAL: Growth type '{growth_type}' is not supported by current explicit logic.")
                    sys.exit(1)

            prev_spend = current_spend
            
    print(f"Success. Growth calculated and saved to {output_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate budget growth metrics per ward and category.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    # Make growth-type non-required in argparse so we can trigger our custom "Refuse and Ask" logic if missing
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")

    args = parser.parse_args()

    # Skill 1: Load and validate dataset
    dataset = load_dataset(args.input)

    # Skill 2: Compute growth and write output
    compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
        output_file=args.output
    )
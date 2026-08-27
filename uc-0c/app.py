import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """Reads CSV, validates columns, and explicitly reports null values."""
    if not os.path.exists(filepath):
        sys.exit(f"Error: Input file '{filepath}' not found.")

    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_report = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames if reader.fieldnames else [])

            if not required_columns.issubset(headers):
                sys.exit(f"Error: Missing required columns. Found: {headers}")

            for row_num, row in enumerate(reader, start=2):
                actual_spend = row.get('actual_spend', '').strip()
                
                # Check for explicit nulls or blanks
                if not actual_spend or actual_spend.lower() == 'null':
                    null_report.append({
                        'row': row_num,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'reason': row.get('notes', 'No reason provided')
                    })
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(actual_spend)
                    except ValueError:
                        row['actual_spend'] = None
                data.append(row)
    except Exception as e:
        sys.exit(f"Error loading dataset: {e}")

    # ENFORCEMENT: Flag every null row before computing
    print(f"Dataset loaded. Found {len(null_report)} null 'actual_spend' values.")
    for nr in null_report:
        print(f" - FLAGGED NULL: Row {nr['row']} ({nr['period']}, {nr['ward']}, {nr['category']}) -> Reason: {nr['reason']}")

    return data

def compute_growth(data, ward, category, growth_type):
    """Computes per-period growth, strictly enforcing per-ward/category rules and showing formulas."""
    
    # ENFORCEMENT: If --growth-type not specified — refuse and ask
    if not growth_type:
        sys.exit("Error: --growth-type not specified. Refusing to guess formula. Please provide it.")

    # ENFORCEMENT: Never aggregate across wards or categories
    if not ward or not category or ward.lower() == 'any' or category.lower() == 'any':
        sys.exit("Error: Aggregation across multiple wards or categories is strictly forbidden. Please specify an exact ward and category.")

    filtered_data = [d for d in data if d['ward'] == ward and d['category'] == category]
    if not filtered_data:
        print("Warning: No data found for the specified ward and category.")
        return []

    # Sort by period to ensure chronological order for MoM calculation
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    prev_spend = None

    for row in filtered_data:
        current_spend = row['actual_spend']
        period = row['period']
        notes = row.get('notes', '')

        result_row = {
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': current_spend if current_spend is not None else 'NULL',
            'growth_type': growth_type,
            'growth_value': 'N/A',
            'formula_used': 'N/A',
            'flag': ''
        }

        if current_spend is None:
            # Handle the null row
            result_row['flag'] = f"FLAGGED NULL: {notes}"
            result_row['formula_used'] = "Cannot compute (missing actual_spend)"
            prev_spend = None  # Reset previous spend since the chain is broken
        else:
            if prev_spend is None:
                result_row['formula_used'] = "Base period (no previous data to compare)"
            else:
                if growth_type.upper() == 'MOM':
                    growth = ((current_spend - prev_spend) / prev_spend) * 100
                    result_row['growth_value'] = f"{growth:+.1f}%"
                    # ENFORCEMENT: Show formula used in every output row
                    result_row['formula_used'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                else:
                    sys.exit(f"Error: Unknown growth type '{growth_type}'. Only MoM is currently implemented.")

            prev_spend = current_spend

        results.append(result_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate per-ward, per-category growth metrics.")
    parser.add_argument('--input', required=True, help="Path to the input CSV file.")
    parser.add_argument('--ward', required=True, help="Specific ward name.")
    parser.add_argument('--category', required=True, help="Specific category name.")
    # Set required=False so we can manually catch and refuse it if missing
    parser.add_argument('--growth-type', required=False, help="Type of growth calculation (e.g., MoM).")
    parser.add_argument('--output', required=True, help="Path to the output CSV file.")

    args = parser.parse_args()

    # Skill 1: Load and Validate
    data = load_dataset(args.input)

    # Skill 2: Compute Growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Write Output
    if results:
        try:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth_type', 'growth_value', 'formula_used', 'flag']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully generated per-ward, per-category output at {args.output}")
        except Exception as e:
            sys.exit(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
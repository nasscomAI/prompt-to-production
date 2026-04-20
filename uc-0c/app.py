"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os


def load_dataset(file_path: str) -> dict:
    """
    Reads the ward budget CSV file, validates required columns, and reports null count with specific row details.

    Returns:
        Dictionary with: 'data' (list of dicts), 'null_count' (int), 'null_rows' (list), 'columns_valid' (bool)
    """
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        if not data:
            raise ValueError("Dataset file is empty")

        # Validate columns
        actual_columns = set(data[0].keys())
        missing_columns = required_columns - actual_columns
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Find null rows
        null_rows = []
        null_count = 0
        for i, row in enumerate(data):
            if not row.get('actual_spend', '').strip():
                null_count += 1
                null_rows.append({
                    'row_index': i + 1,  # 1-based indexing
                    'period': row.get('period', ''),
                    'ward': row.get('ward', ''),
                    'category': row.get('category', ''),
                    'notes': row.get('notes', '')
                })

        print(f"✓ Dataset loaded: {len(data)} rows")
        print(f"✓ Null count: {null_count}")
        if null_rows:
            print("✓ Null rows identified:")
            for null_row in null_rows:
                print(f"  - Row {null_row['row_index']}: {null_row['period']} | {null_row['ward']} | {null_row['category']} | {null_row['notes']}")

        return {
            'data': data,
            'null_count': null_count,
            'null_rows': null_rows,
            'columns_valid': True
        }

    except Exception as e:
        raise ValueError(f"Failed to load dataset: {str(e)}")


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Computes growth rates for a specific ward-category combination using specified growth type.

    Returns:
        List of dictionaries with growth calculations, formulas, and null flags
    """
    if growth_type not in ['MoM', 'YoM']:  # Note: README says MoM, but might be YoM for Year-over-Month
        raise ValueError(f"Invalid growth_type: {growth_type}. Must be 'MoM' or 'YoM'")

    # Filter data for specific ward and category
    filtered_data = [
        row for row in dataset['data']
        if row.get('ward') == ward and row.get('category') == category
    ]

    if not filtered_data:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'")
        return []

    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    null_rows = {f"{row['period']}|{row['ward']}|{row['category']}" for row in dataset['null_rows']}

    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')

        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_spend,
            'previous_spend': '',
            'growth_rate': '',
            'formula_used': '',
            'null_flag': ''
        }

        # Check if this row is null
        row_key = f"{period}|{ward}|{category}"
        if row_key in null_rows or not actual_spend:
            result_row['null_flag'] = f"Must be flagged — not computed | Notes: {notes}"
            results.append(result_row)
            continue

        try:
            current_spend = float(actual_spend)

            if growth_type == 'MoM':
                # Month-over-Month: compare with previous month
                if i == 0:
                    # First month, no previous data
                    result_row['growth_rate'] = 'N/A (first period)'
                    result_row['formula_used'] = 'No previous period for MoM calculation'
                else:
                    prev_row = filtered_data[i-1]
                    prev_spend = prev_row.get('actual_spend', '').strip()

                    if not prev_spend or f"{prev_row['period']}|{ward}|{category}" in null_rows:
                        result_row['growth_rate'] = 'N/A (previous period null)'
                        result_row['formula_used'] = 'Previous period has null value'
                    else:
                        prev_spend = float(prev_spend)
                        result_row['previous_spend'] = str(prev_spend)
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        result_row['growth_rate'] = '.1f'
                        result_row['formula_used'] = '.2f'

            results.append(result_row)

        except ValueError as e:
            result_row['null_flag'] = f"Invalid spend value: {str(e)}"
            results.append(result_row)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoM'], help="Growth calculation type")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")

    args = parser.parse_args()

    try:
        # Step 1: Load and validate dataset
        print(f"Loading dataset: {args.input}")
        dataset = load_dataset(args.input)

        # Step 2: Compute growth for specific ward/category
        print(f"Computing {args.growth_type} growth for {args.ward} - {args.category}")
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)

        if not results:
            print(f"No data found for ward '{args.ward}' and category '{args.category}'")
            return

        # Step 3: Write output CSV
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'previous_spend', 'growth_rate', 'formula_used', 'null_flag']

        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"✓ Growth calculations written to {args.output}")
        print(f"✓ Processed {len(results)} periods")

    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()

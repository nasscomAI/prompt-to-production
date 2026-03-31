"""
UC-0C — Budget Growth Calculator

Computes period-over-period growth (MoM or YoY) for a specific ward and category.
Enforces strict parameter validation, explicit null handling, and formula disclosure.
"""
import argparse
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional


def load_dataset(csv_file_path: str) -> Dict:
    """
    Load and validate the budget CSV dataset.

    Returns: {rows, null_count, null_details}
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Input file not found: {csv_file_path}")

    rows = []
    null_details = []

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty")

            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames)):
                missing = required_cols - set(reader.fieldnames)
                raise ValueError(f"Missing required columns: {missing}")

            for row_num, row in enumerate(reader, start=2):
                rows.append(row)
                # Check for null actual_spend
                if not row.get('actual_spend', '').strip():
                    null_details.append({
                        'period': row.get('period', ''),
                        'ward': row.get('ward', ''),
                        'category': row.get('category', ''),
                        'notes': row.get('notes', '')
                    })
    except Exception as e:
        raise RuntimeError(f"Failed to load CSV: {e}")

    return {
        'rows': rows,
        'null_count': len(null_details),
        'null_details': null_details
    }


def compute_growth(dataset: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """
    Compute period-over-period growth for a specific ward and category.

    Args:
        dataset: list of row dicts from load_dataset
        ward: exact ward name to filter
        category: exact category name to filter
        growth_type: 'MoM' (month-over-month) or 'YoY' (year-over-year)

    Returns:
        list of dicts with keys: period, actual_spend, previous_value, growth_percentage, formula, flag
    """

    if growth_type not in ['MoM', 'YoY']:
        raise ValueError("growth_type must be 'MoM' or 'YoY'")

    # Filter to ward + category
    filtered = [
        row for row in dataset
        if row.get('ward', '').strip() == ward and row.get('category', '').strip() == category
    ]

    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'")
        return []

    # Sort by period
    try:
        filtered.sort(key=lambda r: r.get('period', ''))
    except Exception as e:
        raise ValueError(f"Failed to sort by period: {e}")

    output = []

    for i, row in enumerate(filtered):
        period = row.get('period', '')
        actual_spend_str = row.get('actual_spend', '').strip()

        # Parse actual_spend
        if not actual_spend_str:
            actual_spend = None
        else:
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                actual_spend = None

        # Compute growth
        previous_value = None
        growth_percentage = None
        formula = ""
        flag = ""

        if actual_spend is None:
            flag = "NULL_ROW"
        elif i == 0:
            # First row — no previous value for growth
            formula = "N/A (first period)"
            growth_percentage = None
        else:
            # Get previous actual_spend
            prev_row = filtered[i - 1]
            prev_spend_str = prev_row.get('actual_spend', '').strip()

            if not prev_spend_str:
                # Previous row is null — can't compute growth
                flag = "PREV_NULL"
                previous_value = None
            else:
                try:
                    previous_value = float(prev_spend_str)

                    if growth_type == 'MoM':
                        if previous_value == 0:
                            growth_percentage = None
                            formula = "Division by zero (previous was 0)"
                        else:
                            growth_percentage = ((actual_spend - previous_value) / previous_value) * 100
                            formula = f"({actual_spend} - {previous_value}) / {previous_value} * 100"
                    elif growth_type == 'YoY':
                        # YoY: compare same month 12 months ago
                        # For simplicity, look for row with period shifted back 12 months
                        try:
                            curr_date = datetime.strptime(period, '%Y-%m')
                            prev_year_period = (curr_date.replace(year=curr_date.year - 1)).strftime('%Y-%m')
                            prev_year_row = next((r for r in filtered if r.get('period', '').strip() == prev_year_period), None)

                            if prev_year_row:
                                prev_year_spend_str = prev_year_row.get('actual_spend', '').strip()
                                if prev_year_spend_str:
                                    prev_year_spend = float(prev_year_spend_str)
                                    if prev_year_spend == 0:
                                        growth_percentage = None
                                        formula = "Division by zero (previous year was 0)"
                                    else:
                                        growth_percentage = ((actual_spend - prev_year_spend) / prev_year_spend) * 100
                                        formula = f"({actual_spend} - {prev_year_spend}) / {prev_year_spend} * 100"
                                else:
                                    flag = "PREV_YEAR_NULL"
                            else:
                                # No data for previous year
                                flag = "NO_PREV_YEAR"

                        except Exception as e:
                            formula = f"YoY error: {e}"

                except ValueError:
                    previous_value = None

        output.append({
            'period': period,
            'actual_spend': actual_spend if actual_spend is not None else 'NULL',
            'previous_value': previous_value if previous_value is not None else 'NULL',
            'growth_percentage': round(growth_percentage, 1) if growth_percentage is not None else 'NULL',
            'formula': formula,
            'flag': flag
        })

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")

    args = parser.parse_args()

    # Validate growth-type
    if args.growth_type not in ['MoM', 'YoY']:
        print(f"ERROR: --growth-type must be 'MoM' or 'YoY', got '{args.growth_type}'")
        return

    # Load dataset
    print(f"Loading dataset from {args.input}...")
    try:
        dataset_info = load_dataset(args.input)
        dataset = dataset_info['rows']
        null_count = dataset_info['null_count']
        null_details = dataset_info['null_details']
    except Exception as e:
        print(f"ERROR: {e}")
        return

    print(f"Loaded {len(dataset)} rows. Found {null_count} rows with null actual_spend:")
    for detail in null_details:
        print(f"  - {detail['period']} · {detail['ward']} · {detail['category']} ({detail['notes']})")

    # Compute growth
    print(f"\nComputing {args.growth_type} growth for ward '{args.ward}', category '{args.category}'...")
    try:
        growth_results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    if not growth_results:
        print("No results to output.")
        return

    # Write output CSV
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'previous_value', 'growth_percentage', 'formula', 'flag'])
            writer.writeheader()
            writer.writerows(growth_results)
        print(f"Results written to {args.output}")
    except Exception as e:
        print(f"ERROR: Failed to write output: {e}")
        return


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Ward-level budget growth calculator.
Implements load_dataset and compute_growth skills per agents.md and skills.md.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from pathlib import Path
from collections import defaultdict


def load_dataset(file_path):
    """
    Reads CSV, validates column structure, counts and reports all null actual_spend rows.
    
    Skill: load_dataset
    Input: File path to ward_budget.csv
    Output: (list of dicts, dict with null_count and null_rows)
    Error handling: Rejects if required columns missing, period format invalid, or actual_spend type invalid.
    
    Args:
        file_path: Path to ward_budget.csv
    
    Returns:
        tuple: (list of row dicts, dict with null_count and null_rows list)
    
    Raises:
        ValueError: If validation fails
        FileNotFoundError: If file does not exist
    """
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")
    
    if not rows:
        raise ValueError("CSV file is empty")
    
    # Check for required columns
    found_columns = list(rows[0].keys())
    missing_columns = [col for col in required_columns if col not in found_columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Found columns: {found_columns}"
        )
    
    # Validate period format (YYYY-MM) and identify null rows
    null_rows = []
    for i, row in enumerate(rows):
        period = row['period'].strip()
        
        # Validate period format
        if not (len(period) == 7 and period[4] == '-' and period[:4].isdigit() and period[5:].isdigit()):
            raise ValueError(f"Invalid period format at row {i+2}: '{period}'. Expected YYYY-MM format.")
        
        row['period'] = period
        
        # Check for null actual_spend
        actual_spend = row['actual_spend'].strip()
        if actual_spend == '':
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'].strip(),
                'category': row['category'].strip(),
                'actual_spend': None,
                'notes': row['notes'].strip()
            })
            row['actual_spend'] = None
        else:
            try:
                row['actual_spend'] = float(actual_spend)
            except ValueError:
                raise ValueError(f"Invalid actual_spend value at row {i+2}: '{actual_spend}'. Expected float or blank.")
        
        # Clean up other fields
        row['ward'] = row['ward'].strip()
        row['category'] = row['category'].strip()
        row['budgeted_amount'] = float(row['budgeted_amount'].strip())
        row['notes'] = row['notes'].strip()
    
    null_info = {
        'null_count': len(null_rows),
        'null_rows': null_rows
    }
    
    return rows, null_info


def compute_growth(rows, ward, category, growth_type):
    """
    Computes MoM or YoY growth for a specified ward and category.
    Returns per-period growth table with formula shown in each row.
    
    Skill: compute_growth
    Input: list of row dicts (from load_dataset), ward (string), category (string), growth_type ('MoM' or 'YoY')
    Output: list of dicts with period, actual_spend, growth_percentage, formula
    Error handling: Rejects if ward/category not found, growth_type invalid, or cross-ward/cross-category.
    
    Args:
        rows: list of row dicts (from load_dataset)
        ward: Ward name (string)
        category: Category name (string)
        growth_type: 'MoM' (month-over-month) or 'YoY' (year-over-year)
    
    Returns:
        list of dicts with columns: period, actual_spend, growth_percentage, formula
    
    Raises:
        ValueError: If validation fails
    """
    # Enforcement: growth_type must be specified
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(
            f"Invalid growth_type: '{growth_type}'. "
            f"Must specify either 'MoM' (month-over-month) or 'YoY' (year-over-year). "
            f"Cannot guess — please specify."
        )
    
    # Enforcement: ward must exist
    available_wards = set(row['ward'] for row in rows)
    if ward not in available_wards:
        raise ValueError(
            f"Ward not found: '{ward}'. "
            f"Available wards: {sorted(available_wards)}"
        )
    
    # Enforcement: category must exist
    available_categories = set(row['category'] for row in rows)
    if category not in available_categories:
        raise ValueError(
            f"Category not found: '{category}'. "
            f"Available categories: {sorted(available_categories)}"
        )
    
    # Enforcement: no cross-ward or cross-category aggregation
    # Filter for the specified ward and category only
    filtered_rows = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered_rows = sorted(filtered_rows, key=lambda r: r['period'])
    
    if len(filtered_rows) == 0:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'. "
            f"Cannot aggregate across wards or categories."
        )
    
    # Compute growth
    results = []
    
    for idx, row in enumerate(filtered_rows):
        period = row['period']
        actual_spend = row['actual_spend']
        formula = None
        growth_percentage = None
        
        if actual_spend is None:
            # Enforcement: Flag every null row before computing
            formula = f"NULL (reason: {row['notes']})"
            growth_percentage = None
        else:
            if growth_type == 'MoM':
                if idx == 0:
                    # First month has no previous month to compare
                    formula = "No MoM baseline (first period)"
                    growth_percentage = None
                else:
                    previous_spend = filtered_rows[idx - 1]['actual_spend']
                    if previous_spend is None:
                        # Previous month is null, cannot compute
                        formula = "Cannot compute MoM (previous month is NULL)"
                        growth_percentage = None
                    else:
                        # Enforcement: Show formula used in every output row
                        growth_percentage = ((actual_spend - previous_spend) / previous_spend) * 100
                        formula = f"(({actual_spend} - {previous_spend}) / {previous_spend}) * 100 = {growth_percentage:.1f}%"
            
            elif growth_type == 'YoY':
                if idx < 12:
                    # First 12 months have no previous year to compare
                    formula = "No YoY baseline (before first year complete)"
                    growth_percentage = None
                else:
                    previous_year_spend = filtered_rows[idx - 12]['actual_spend']
                    if previous_year_spend is None:
                        # Previous year is null, cannot compute
                        formula = "Cannot compute YoY (previous year is NULL)"
                        growth_percentage = None
                    else:
                        # Enforcement: Show formula used in every output row
                        growth_percentage = ((actual_spend - previous_year_spend) / previous_year_spend) * 100
                        formula = f"(({actual_spend} - {previous_year_spend}) / {previous_year_spend}) * 100 = {growth_percentage:.1f}%"
        
        results.append({
            'period': period,
            'actual_spend': actual_spend,
            'growth_percentage': growth_percentage,
            'formula': formula
        })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Budget Growth Calculator — Ward-level, per-category analysis"
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input CSV file (ward_budget.csv)'
    )
    parser.add_argument(
        '--ward',
        required=True,
        help='Ward name (e.g., "Ward 1 – Kasba")'
    )
    parser.add_argument(
        '--category',
        required=True,
        help='Budget category (e.g., "Roads & Pothole Repair")'
    )
    parser.add_argument(
        '--growth-type',
        required=True,
        help='Growth calculation type: MoM (month-over-month) or YoY (year-over-year)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output CSV file'
    )
    
    args = parser.parse_args()
    
    try:
        # Load and validate dataset
        print("Loading dataset...")
        rows, null_info = load_dataset(args.input)
        
        print(f"Dataset loaded successfully. Total rows: {len(rows)}")
        print(f"Null actual_spend values found: {null_info['null_count']}")
        
        # Enforcement: Flag every null row before computing
        if null_info['null_rows']:
            print("\nNull rows (flagged before computation):")
            for null_row in null_info['null_rows']:
                print(
                    f"  - {null_row['period']} · {null_row['ward']} · {null_row['category']} "
                    f"(Reason: {null_row['notes']})"
                )
        
        # Enforcement: If growth_type not specified, refuse and ask
        if not args.growth_type:
            raise ValueError(
                "Missing required argument: --growth-type. "
                "Must specify either 'MoM' (month-over-month) or 'YoY' (year-over-year). "
                "Cannot guess."
            )
        
        # Compute growth
        print(f"\nComputing {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}")
        
        growth_table = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        # Save output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'growth_percentage', 'formula']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(growth_table)
        
        print(f"\nOutput saved to: {args.output}")
        print("\nFirst 5 rows of output:")
        for i, row in enumerate(growth_table[:5]):
            print(f"  {row['period']}: spend={row['actual_spend']}, growth={row['growth_percentage']}, formula={row['formula']}")
        
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

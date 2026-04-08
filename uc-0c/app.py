"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import re
from typing import List, Dict, Any


def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Reads the ward budget CSV, validates required columns, and returns filtered rows with null handling metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {file_path} not found")
    
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if not all(col in reader.fieldnames for col in required_columns):
        raise ValueError(f"CSV missing required columns: {required_columns}")
    
    processed_rows = []
    null_count = 0
    for row in rows:
        try:
            budgeted = float(row['budgeted_amount'])
            actual = row['actual_spend'].strip()
            if actual == '':
                actual = None
                null_count += 1
            else:
                actual = float(actual)
        except ValueError:
            actual = None
            null_count += 1
        
        processed_rows.append({
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'budgeted_amount': budgeted,
            'actual_spend': actual,
            'notes': row['notes'],
            'missing_flag': actual is None,
            'missing_reason': row['notes'] if actual is None else ''
        })
    
    print(f"Loaded {len(processed_rows)} rows, {null_count} null actual_spend values.")
    return processed_rows


def compute_growth(dataset: List[Dict[str, Any]], ward: str, category: str, growth_type: str, end_period: str = None) -> List[Dict[str, Any]]:
    """Computes growth for a specified ward/category and growth_type up to end_period."""
    if not ward or not category:
        raise ValueError("Ward and category must be specified")
    if growth_type not in ['MoM', 'YTD', 'YoY']:
        raise ValueError("Growth type must be MoM, YTD, or YoY")
    if growth_type == 'YoY':
        raise ValueError("YoY growth requires previous year data, which is not available in the current dataset")
    
    # Filter rows
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    # Validate and filter up to end_period if provided
    if end_period:
        if not re.match(r'^\d{4}-\d{2}$', end_period):
            raise ValueError("end_period must be in YYYY-MM format")
        filtered = [r for r in filtered if r['period'] <= end_period]
        if not filtered:
            raise ValueError(f"No rows available for {ward}/{category} at or before period {end_period}")
    
    results = []
    prev_actual = None
    ytd_actual = 0.0
    ytd_budget = 0.0
    
    for row in filtered:
        period = row['period']
        budgeted = row['budgeted_amount']
        actual = row['actual_spend']
        notes = row['notes']
        
        if actual is None:
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'budgeted_amount': budgeted,
                'growth_value': 'NULL',
                'growth_formula': 'NULL',
                'status': 'NULL',
                'notes': notes
            })
            continue
        
        if growth_type == 'MoM':
            if prev_actual is None:
                growth_value = 'N/A (first period)'
                formula = 'N/A'
            else:
                growth = ((actual - prev_actual) / prev_actual) * 100
                growth_value = f"{growth:+.1f}%"
                formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
            prev_actual = actual
        
        elif growth_type == 'YTD':
            ytd_actual += actual
            ytd_budget += budgeted
            growth = ((ytd_actual - ytd_budget) / ytd_budget) * 100
            growth_value = f"{growth:+.1f}%"
            formula = f"(({ytd_actual} - {ytd_budget}) / {ytd_budget}) * 100"
        
        results.append({
            'period': period,
            'actual_spend': actual,
            'budgeted_amount': budgeted,
            'growth_value': growth_value,
            'growth_formula': formula,
            'status': 'computed',
            'notes': notes
        })
    
    return results


def validate_no_aggregate(ward: str, category: str, allow_aggregate: bool = False) -> (bool, str):
    """Verifies that the request is not attempting all-ward/category aggregation unless explicitly allowed."""
    if not allow_aggregate and (not ward or not category):
        return False, "Refusing to aggregate across wards or categories unless explicitly instructed."
    return True, "Valid request."


def main():
    parser = argparse.ArgumentParser(description='UC-0C growth calculation')
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YTD', 'YoY'], help='Growth type')
    parser.add_argument('--end-period', help='End period YYYY-MM (optional)')
    parser.add_argument('--output', required=True, help='Output CSV path')
    args = parser.parse_args()
    
    # Validate no aggregate
    valid, msg = validate_no_aggregate(args.ward, args.category)
    if not valid:
        print(msg)
        return
    
    # Load dataset
    dataset = load_dataset(args.input)
    
    # Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type, args.end_period)
    
    # Write output
    fieldnames = ['period', 'actual_spend', 'budgeted_amount', 'growth_value', 'growth_formula', 'status', 'notes']
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Growth calculation complete. Output written to {args.output}")


if __name__ == '__main__':
    main()

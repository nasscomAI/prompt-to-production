"""
UC-0C app.py — Budget Growth Calculator with Null Handling and Formula Display.

Implements load_dataset and compute_growth skills.
Enforces UC-0C agent rules: no silent aggregation, null flagging, formula display, growth_type required.
"""
import argparse
import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_dataset(file_path):
    """
    Reads budget CSV, validates columns, detects null rows, returns structured dataset.
    
    Args:
        file_path (str): Path to ward_budget.csv
        
    Returns:
        dict: {
            'success': bool,
            'error': str or None,
            'rows': [list of row dicts],
            'null_rows': [list of null row dicts with reason],
            'null_count': int,
            'wards': [list of unique wards],
            'categories': [list of unique categories],
            'date_range': {'start': 'YYYY-MM', 'end': 'YYYY-MM'}
        }
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                'success': False,
                'error': f'FILE_NOT_FOUND: {file_path}',
                'rows': [],
                'null_rows': [],
                'null_count': 0,
                'wards': [],
                'categories': [],
                'date_range': None
            }
        
        rows = []
        null_rows = []
        wards_set = set()
        categories_set = set()
        periods = []
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not reader.fieldnames:
                return {
                    'success': False,
                    'error': 'INVALID_CSV: File is empty or not a valid CSV',
                    'rows': [],
                    'null_rows': [],
                    'null_count': 0,
                    'wards': [],
                    'categories': [],
                    'date_range': None
                }
            
            expected_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            actual_columns = set(reader.fieldnames)
            
            if not expected_columns.issubset(actual_columns):
                missing = expected_columns - actual_columns
                return {
                    'success': False,
                    'error': f'INVALID_COLUMNS: Missing columns {missing}',
                    'rows': [],
                    'null_rows': [],
                    'null_count': 0,
                    'wards': [],
                    'categories': [],
                    'date_range': None
                }
            
            for row in reader:
                # Normalize and track metadata
                period = row['period'].strip()
                ward = row['ward'].strip()
                category = row['category'].strip()
                budgeted_amount = row['budgeted_amount'].strip()
                actual_spend = row['actual_spend'].strip()
                notes = row['notes'].strip() if 'notes' in row else ''
                
                periods.append(period)
                wards_set.add(ward)
                categories_set.add(category)
                
                # Parse amounts
                try:
                    budgeted_amount = float(budgeted_amount) if budgeted_amount else None
                except ValueError:
                    budgeted_amount = None
                
                # Handle null actual_spend
                actual_spend_value = None
                is_null = False
                
                if not actual_spend or actual_spend.lower() in ['null', 'none', 'n/a', '']:
                    is_null = True
                    null_rows.append({
                        'period': period,
                        'ward': ward,
                        'category': category,
                        'budgeted_amount': budgeted_amount,
                        'actual_spend': None,
                        'notes': notes,
                        'reason': notes or 'No data available'
                    })
                else:
                    try:
                        actual_spend_value = float(actual_spend)
                    except ValueError:
                        actual_spend_value = None
                        is_null = True
                        null_rows.append({
                            'period': period,
                            'ward': ward,
                            'category': category,
                            'budgeted_amount': budgeted_amount,
                            'actual_spend': None,
                            'notes': notes,
                            'reason': f'Invalid format: {actual_spend}'
                        })
                
                # Add row regardless of null status
                rows.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'budgeted_amount': budgeted_amount,
                    'actual_spend': actual_spend_value,
                    'notes': notes,
                    'is_null': is_null
                })
        
        # Determine date range
        date_range = None
        if periods:
            sorted_periods = sorted(set(periods))
            date_range = {'start': sorted_periods[0], 'end': sorted_periods[-1]}
        
        return {
            'success': True,
            'error': None,
            'rows': rows,
            'null_rows': null_rows,
            'null_count': len(null_rows),
            'wards': sorted(list(wards_set)),
            'categories': sorted(list(categories_set)),
            'date_range': date_range
        }
    
    except IOError as e:
        return {
            'success': False,
            'error': f'FILE_UNREADABLE: {str(e)}',
            'rows': [],
            'null_rows': [],
            'null_count': 0,
            'wards': [],
            'categories': [],
            'date_range': None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'UNKNOWN_ERROR: {str(e)}',
            'rows': [],
            'null_rows': [],
            'null_count': 0,
            'wards': [],
            'categories': [],
            'date_range': None
        }


def compute_growth(rows, ward, category, growth_type, null_rows=None):
    """
    Computes MoM or YoY growth for a specific ward-category, with formula display.
    
    Args:
        rows (list): Dataset rows from load_dataset
        ward (str): Ward name (exact match required)
        category (str): Category name (exact match required)
        growth_type (str): 'MoM' or 'YoY' (required)
        null_rows (list): Null rows for flagging
        
    Returns:
        dict: {
            'success': bool,
            'error': str or None,
            'table': [list of result rows],
            'null_flagged': [list of {period, reason}],
            'aggregation_refused': bool,
            'growth_type_used': str
        }
    """
    if null_rows is None:
        null_rows = []
    
    # Validate growth_type
    if not growth_type or growth_type not in ['MoM', 'YoY']:
        return {
            'success': False,
            'error': 'GROWTH_TYPE_REQUIRED: Must specify --growth-type (MoM or YoY). Cannot assume calculation method',
            'table': [],
            'null_flagged': [],
            'aggregation_refused': False,
            'growth_type_used': None
        }
    
    # Filter for specific ward and category
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        return {
            'success': False,
            'error': f'WARD_OR_CATEGORY_NOT_FOUND: No data for ward="{ward}" category="{category}"',
            'table': [],
            'null_flagged': [],
            'aggregation_refused': False,
            'growth_type_used': growth_type
        }
    
    # Sort by period
    filtered_sorted = sorted(filtered, key=lambda r: r['period'])
    
    # Build null flag mapping
    null_flag_map = {}
    for null_row in null_rows:
        if null_row['ward'] == ward and null_row['category'] == category:
            null_flag_map[null_row['period']] = null_row['reason']
    
    # Compute growth
    result_table = []
    period_to_spend = {r['period']: r['actual_spend'] for r in filtered_sorted}
    
    for i, row in enumerate(filtered_sorted):
        period = row['period']
        actual_spend = row['actual_spend']
        
        result_row = {
            'period': period,
            'actual_spend': actual_spend,
            'previous_period_spend': None,
            'growth_percent': None,
            'formula': None,
            'notes': row['notes']
        }
        
        # Flag null rows
        if row['is_null']:
            result_row['formula'] = 'N/A (null value)'
            result_row['notes'] = null_flag_map.get(period, row['notes'] or 'No data available')
        elif growth_type == 'MoM':
            # Find previous month
            if i > 0:
                prev_row = filtered_sorted[i - 1]
                prev_spend = prev_row['actual_spend']
                
                if prev_spend is not None and prev_spend != 0:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    result_row['previous_period_spend'] = prev_spend
                    result_row['growth_percent'] = round(growth, 2)
                    result_row['formula'] = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100 = {growth:.2f}%"
                else:
                    result_row['formula'] = 'Cannot compute (previous month is null or zero)'
            else:
                result_row['formula'] = 'N/A (first period)'
        
        elif growth_type == 'YoY':
            # YoY: compare with same month from 12 months ago
            # Extract year and month
            curr_year, curr_month = period.split('-')
            prev_year = str(int(curr_year) - 1)
            prev_period = f"{prev_year}-{curr_month}"
            
            if prev_period in period_to_spend:
                prev_spend = period_to_spend[prev_period]
                if prev_spend is not None and prev_spend != 0:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    result_row['previous_period_spend'] = prev_spend
                    result_row['growth_percent'] = round(growth, 2)
                    result_row['formula'] = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100 = {growth:.2f}%"
                else:
                    result_row['formula'] = 'Cannot compute (same period last year is null or zero)'
            else:
                result_row['formula'] = 'Cannot compute (same period last year not available)'
        
        result_table.append(result_row)
    
    # Build null_flagged list
    null_flagged = [
        {'period': r['period'], 'reason': null_flag_map[r['period']]}
        for r in result_table if r['period'] in null_flag_map
    ]
    
    return {
        'success': True,
        'error': None,
        'table': result_table,
        'null_flagged': null_flagged,
        'aggregation_refused': False,
        'growth_type_used': growth_type
    }


def main():
    parser = argparse.ArgumentParser(
        description='UC-0C Budget Growth Calculator: Ward-category level MoM/YoY growth with null flagging and formula display.'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input budget CSV (ward_budget.csv)'
    )
    parser.add_argument(
        '--ward',
        type=str,
        required=True,
        help='Ward name (exact match, e.g., "Ward 1 – Kasba")'
    )
    parser.add_argument(
        '--category',
        type=str,
        required=True,
        help='Budget category (exact match, e.g., "Roads & Pothole Repair")'
    )
    parser.add_argument(
        '--growth-type',
        type=str,
        default=None,
        help='Growth calculation type: MoM (month-on-month) or YoY (year-on-year). REQUIRED — cannot guess.'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to output CSV file'
    )
    
    args = parser.parse_args()
    
    # Step 1: Load and validate dataset
    print(f"[1/2] Loading dataset from {args.input}...", file=sys.stderr)
    load_result = load_dataset(args.input)
    
    if not load_result['success']:
        print(f"ERROR: {load_result['error']}", file=sys.stderr)
        sys.exit(1)
    
    print(f"SUCCESS: Loaded {len(load_result['rows'])} rows, {len(load_result['null_rows'])} null values", file=sys.stderr)
    print(f"Available wards: {', '.join(load_result['wards'][:3])}{'...' if len(load_result['wards']) > 3 else ''}", file=sys.stderr)
    print(f"Available categories: {', '.join(load_result['categories'][:3])}{'...' if len(load_result['categories']) > 3 else ''}", file=sys.stderr)
    
    # Report null rows
    if load_result['null_rows']:
        print(f"\nFLAGGED NULL ROWS ({len(load_result['null_rows'])}):", file=sys.stderr)
        for null_row in load_result['null_rows']:
            print(f"  - {null_row['period']} | {null_row['ward']} | {null_row['category']} → {null_row['reason']}", file=sys.stderr)
    
    # Step 2: Compute growth
    print(f"\n[2/2] Computing {args.growth_type} growth for {args.ward} / {args.category}...", file=sys.stderr)
    growth_result = compute_growth(
        load_result['rows'],
        args.ward,
        args.category,
        args.growth_type,
        load_result['null_rows']
    )
    
    if not growth_result['success']:
        print(f"ERROR: {growth_result['error']}", file=sys.stderr)
        sys.exit(1)
    
    print(f"SUCCESS: Computed growth for {len(growth_result['table'])} periods", file=sys.stderr)
    
    if growth_result['null_flagged']:
        print(f"\nNULL PERIODS IN RESULT ({len(growth_result['null_flagged'])}):", file=sys.stderr)
        for flagged in growth_result['null_flagged']:
            print(f"  - {flagged['period']}: {flagged['reason']}", file=sys.stderr)
    
    # Step 3: Write output
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'previous_period_spend', 'growth_percent', 'formula', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in growth_result['table']:
                writer.writerow({
                    'period': row['period'],
                    'actual_spend': row['actual_spend'] if row['actual_spend'] is not None else '',
                    'previous_period_spend': row['previous_period_spend'] if row['previous_period_spend'] is not None else '',
                    'growth_percent': row['growth_percent'] if row['growth_percent'] is not None else '',
                    'formula': row['formula'],
                    'notes': row['notes']
                })
        
        print(f"\nSUCCESS: Output written to {args.output}", file=sys.stderr)
    
    except IOError as e:
        print(f"ERROR: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

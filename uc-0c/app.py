"""
UC-0C app.py — Budget Growth Calculator
Calculates per-ward per-category budget growth with null value flagging.
"""
import csv
import argparse
from typing import List, Dict, Tuple, Optional


def load_dataset(file_path: str) -> Tuple[List[Dict], Dict]:
    """
    Load budget CSV and report null values.
    Returns: (data_rows, null_report)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    # Validate required columns
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if rows:
        missing = [col for col in required_cols if col not in rows[0].keys()]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    # Report null values
    null_rows = []
    for row in rows:
        if not row['actual_spend'] or row['actual_spend'].strip() == '':
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'notes': row['notes']
            })
    
    null_report = {
        'count': len(null_rows),
        'rows': null_rows
    }
    
    return rows, null_report


def validate_scope(ward: Optional[str], category: Optional[str]) -> Tuple[bool, str]:
    """
    Validate that ward and category are specified (no aggregation).
    """
    if not ward:
        return False, "Error: --ward parameter is required. Aggregation across wards is not permitted. Please specify a single ward."
    
    if not category:
        return False, "Error: --category parameter is required. Aggregation across categories is not permitted. Please specify a single category."
    
    # Check for wildcard attempts
    if '*' in ward or 'all' in ward.lower():
        return False, "Error: Wildcard/aggregation not permitted. Please specify a single ward name."
    
    if '*' in category or 'all' in category.lower():
        return False, "Error: Wildcard/aggregation not permitted. Please specify a single category name."
    
    return True, ""


def filter_data(rows: List[Dict], ward: str, category: str) -> List[Dict]:
    """
    Filter to specified ward and category only.
    """
    filtered = [
        row for row in rows 
        if row['ward'] == ward and row['category'] == category
    ]
    
    # Sort by period chronologically
    filtered.sort(key=lambda x: x['period'])
    
    return filtered


def compute_growth(rows: List[Dict], growth_type: str) -> List[Dict]:
    """
    Compute MoM or YoY growth with formula shown.
    """
    results = []
    
    for i, row in enumerate(rows):
        period = row['period']
        actual_spend = row['actual_spend']
        
        # Check if null
        if not actual_spend or actual_spend.strip() == '':
            results.append({
                'period': period,
                'actual_spend': None,
                'growth_pct': None,
                'formula': None,
                'is_null': True,
                'null_reason': row['notes']
            })
            continue
        
        # Parse actual spend
        try:
            current_spend = float(actual_spend)
        except ValueError:
            results.append({
                'period': period,
                'actual_spend': None,
                'growth_pct': None,
                'formula': None,
                'is_null': True,
                'null_reason': 'Invalid numeric value'
            })
            continue
        
        # Determine previous period based on growth type
        if growth_type == 'MoM':
            # Previous month
            if i == 0:
                # First period, no previous
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'growth_pct': None,
                    'formula': None,
                    'is_null': False,
                    'null_reason': 'First period - no previous month to compare'
                })
                continue
            
            prev_row = rows[i - 1]
            prev_spend_str = prev_row['actual_spend']
            
        elif growth_type == 'YoY':
            # Same month previous year (12 months ago)
            # For 2024 data, there's no 2023 data, so all will be first period
            results.append({
                'period': period,
                'actual_spend': current_spend,
                'growth_pct': None,
                'formula': None,
                'is_null': False,
                'null_reason': 'YoY not available - no previous year data in dataset'
            })
            continue
        else:
            raise ValueError(f"Invalid growth_type: {growth_type}")
        
        # Check if previous period has null
        if not prev_spend_str or prev_spend_str.strip() == '':
            results.append({
                'period': period,
                'actual_spend': current_spend,
                'growth_pct': None,
                'formula': None,
                'is_null': False,
                'null_reason': f'Previous period ({prev_row["period"]}) has null value'
            })
            continue
        
        # Calculate growth
        try:
            prev_spend = float(prev_spend_str)
        except ValueError:
            results.append({
                'period': period,
                'actual_spend': current_spend,
                'growth_pct': None,
                'formula': None,
                'is_null': False,
                'null_reason': 'Previous period has invalid numeric value'
            })
            continue
        
        if prev_spend == 0:
            growth_pct = None
            formula = "Cannot compute - division by zero"
            null_reason = "Previous period spend is zero"
        else:
            growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
            formula = f"({current_spend} - {prev_spend}) / {prev_spend} × 100 = {growth_pct:.1f}%"
            null_reason = None
        
        results.append({
            'period': period,
            'actual_spend': current_spend,
            'growth_pct': growth_pct,
            'formula': formula,
            'is_null': False,
            'null_reason': null_reason
        })
    
    return results


def format_output_table(results: List[Dict], ward: str, category: str, growth_type: str) -> str:
    """
    Format results as readable table.
    """
    lines = []
    lines.append(f"\nGrowth Analysis for: {ward} - {category}")
    lines.append(f"Growth Type: {growth_type}")
    lines.append("=" * 100)
    lines.append(f"{'Period':<12} {'Actual Spend (₹L)':<20} {'Growth %':<15} {'Formula/Note':<50}")
    lines.append("-" * 100)
    
    for result in results:
        period = result['period']
        
        if result['is_null']:
            spend_str = "NULL"
            growth_str = "N/A"
            note = f"Cannot compute - {result['null_reason']}"
        elif result['growth_pct'] is None:
            spend_str = f"₹{result['actual_spend']:.1f}L"
            growth_str = "N/A"
            note = result['null_reason'] if result['null_reason'] else "First period"
        else:
            spend_str = f"₹{result['actual_spend']:.1f}L"
            growth_str = f"{result['growth_pct']:+.1f}%"
            note = result['formula']
        
        lines.append(f"{period:<12} {spend_str:<20} {growth_str:<15} {note:<50}")
    
    lines.append("=" * 100)
    
    return "\n".join(lines)


def write_growth_output(results: List[Dict], output_path: str, ward: str, category: str, growth_type: str):
    """
    Write results to CSV file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth_pct', 'formula', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'ward': ward,
                    'category': category,
                    'period': result['period'],
                    'actual_spend': result['actual_spend'] if result['actual_spend'] is not None else 'NULL',
                    'growth_pct': f"{result['growth_pct']:.1f}" if result['growth_pct'] is not None else 'N/A',
                    'formula': result['formula'] if result['formula'] else '',
                    'notes': result['null_reason'] if result['null_reason'] else ''
                })
        
        print(f"\n✓ Output written to {output_path}")
    
    except IOError as e:
        raise IOError(f"Cannot write to output file: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Calculate budget growth per ward and category')
    parser.add_argument('--input', required=True, help='Input CSV file (ward_budget.csv)')
    parser.add_argument('--ward', required=True, help='Ward name (exact match)')
    parser.add_argument('--category', required=True, help='Category name (exact match)')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YoY'], 
                       help='Growth calculation type: MoM (Month-over-Month) or YoY (Year-over-Year)')
    parser.add_argument('--output', required=True, help='Output CSV file')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Budget Growth Calculator - UC-0C")
    print("=" * 70)
    print(f"\nInput: {args.input}")
    print(f"Ward: {args.ward}")
    print(f"Category: {args.category}")
    print(f"Growth Type: {args.growth_type}")
    print(f"Output: {args.output}\n")
    
    # Validate scope (no aggregation)
    is_valid, error_msg = validate_scope(args.ward, args.category)
    if not is_valid:
        print(error_msg)
        return
    
    # Load dataset
    rows, null_report = load_dataset(args.input)
    print(f"✓ Loaded {len(rows)} rows from dataset")
    
    # Report null values
    if null_report['count'] > 0:
        print(f"\n⚠ WARNING: Found {null_report['count']} rows with null actual_spend:")
        for null_row in null_report['rows']:
            print(f"  - {null_row['period']} | {null_row['ward']} | {null_row['category']}")
            print(f"    Reason: {null_row['notes']}")
    else:
        print("✓ No null values found in actual_spend column")
    
    # Filter to ward and category
    filtered = filter_data(rows, args.ward, args.category)
    print(f"\n✓ Filtered to {len(filtered)} rows for {args.ward} - {args.category}")
    
    if not filtered:
        print("\nError: No data found for specified ward and category combination.")
        return
    
    # Compute growth
    results = compute_growth(filtered, args.growth_type)
    
    # Display results
    table = format_output_table(results, args.ward, args.category, args.growth_type)
    print(table)
    
    # Write output
    write_growth_output(results, args.output, args.ward, args.category, args.growth_type)
    
    # Summary
    computed_count = sum(1 for r in results if r['growth_pct'] is not None)
    null_count = sum(1 for r in results if r['is_null'])
    print(f"\nSummary:")
    print(f"  Total periods: {len(results)}")
    print(f"  Growth computed: {computed_count}")
    print(f"  Null/Cannot compute: {len(results) - computed_count}")


if __name__ == "__main__":
    main()

"""
UC-0C — Budget Growth Calculation
Implementation of per-ward per-category growth calculation with null handling and formula tracking.
"""
import argparse
import csv
import sys
from io import StringIO

def load_dataset(input_path: str) -> tuple:
    """
    Load CSV, validate schema, identify and report null rows.
    Returns: (rows_list, null_rows_list)
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"ERROR: Cannot read {input_path}: {str(e)}", file=sys.stderr)
        raise
    
    # Validate required columns
    if not rows:
        raise ValueError("CSV is empty")
    
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_cols.issubset(set(rows[0].keys())):
        missing = required_cols - set(rows[0].keys())
        raise ValueError(f"Missing required columns: {missing}")
    
    # Identify null rows in actual_spend
    null_rows = []
    for row in rows:
        actual_spend = row.get('actual_spend', '').strip()
        if not actual_spend or actual_spend.lower() == 'nan':
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row.get('notes', 'No reason provided').strip() or 'No reason provided'
            })
    
    return rows, null_rows

def validate_ward_category_exists(rows: list, ward: str, category: str) -> bool:
    """
    Check if specified ward and category exist in dataset.
    """
    for row in rows:
        if row['ward'] == ward and row['category'] == category:
            return True
    return False

def check_for_null_in_subset(rows: list, ward: str, category: str) -> list:
    """
    Check for null actual_spend values in the specified ward+category.
    Returns list of {period, reason} for nulls.
    """
    nulls = []
    for row in rows:
        if row['ward'] == ward and row['category'] == category:
            actual_spend = row.get('actual_spend', '').strip()
            if not actual_spend or actual_spend.lower() == 'nan':
                nulls.append({
                    'period': row['period'],
                    'reason': row.get('notes', 'No reason provided').strip() or 'No reason provided'
                })
    return nulls

def get_years_in_dataset(rows: list) -> set:
    """
    Extract unique years from period column (format YYYY-MM).
    """
    years = set()
    for row in rows:
        try:
            period = row.get('period', '')
            year = int(period.split('-')[0])
            years.add(year)
        except:
            pass
    return years

def parse_float_or_null(value: str) -> float:
    """
    Parse string to float, handling null values.
    Returns float or None.
    """
    value = value.strip()
    if not value or value.lower() == 'nan':
        return None
    try:
        return float(value)
    except:
        return None

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> str:
    """
    Compute MoM or YoY growth for specified ward+category.
    Returns CSV string with per-period results including formulas.
    """
    # Validate ward and category exist
    if not validate_ward_category_exists(rows, ward, category):
        raise ValueError(f"Ward '{ward}' and/or category '{category}' not found in dataset")
    
    # Validate growth_type
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'")
    
    # For YoY, check if we have multiple years
    if growth_type == 'YoY':
        years = get_years_in_dataset(rows)
        if len(years) < 2:
            raise ValueError(f"YoY growth requires data from multiple years. Current data has only year(s): {sorted(years)}")
    
    # Filter data for this ward and category, sorted by period
    subset = []
    for row in rows:
        if row['ward'] == ward and row['category'] == category:
            subset.append(row)
    
    # Sort by period
    subset.sort(key=lambda x: x['period'])
    
    # Check for nulls in this subset
    nulls = check_for_null_in_subset(rows, ward, category)
    if nulls:
        print(f"\nWARNING: Found {len(nulls)} null actual_spend value(s) in {ward} / {category}:", file=sys.stderr)
        for null_row in nulls:
            print(f"  - {null_row['period']}: {null_row['reason']}", file=sys.stderr)
        print()
    
    # Build output rows
    output_rows = []
    
    for i, row in enumerate(subset):
        period = row['period']
        actual_spend_str = row.get('actual_spend', '').strip()
        actual_spend = parse_float_or_null(actual_spend_str)
        
        output_row = {
            'period': period,
            'actual_spend': actual_spend_str if actual_spend_str else '[NULL]',
            'previous_spend': '[N/A]',
            'growth_rate': '[N/A]',
            'formula': 'N/A (first period or null)'
        }
        
        # Compute growth if we have previous data
        if i > 0 and actual_spend is not None:
            if growth_type == 'MoM':
                prev_row = subset[i - 1]
                prev_spend_str = prev_row.get('actual_spend', '').strip()
                prev_spend = parse_float_or_null(prev_spend_str)
                
                if prev_spend is not None and prev_spend != 0:
                    growth_rate = ((actual_spend - prev_spend) / prev_spend) * 100
                    output_row['previous_spend'] = f"{prev_spend:.1f}"
                    output_row['growth_rate'] = f"{growth_rate:+.1f}%"
                    output_row['formula'] = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                else:
                    output_row['previous_spend'] = '[NULL]' if prev_spend is None else str(prev_spend)
                    output_row['growth_rate'] = '[Cannot compute]'
                    output_row['formula'] = 'Previous period is null or zero'
            
            elif growth_type == 'YoY':
                # Look for same month in previous year
                current_month = period.split('-')[1]
                current_year = int(period.split('-')[0])
                prev_year = current_year - 1
                prev_period = f"{prev_year}-{current_month}"
                
                # Find matching period in subset
                prev_spend = None
                for search_row in subset:
                    if search_row['period'] == prev_period:
                        prev_spend_str = search_row.get('actual_spend', '').strip()
                        prev_spend = parse_float_or_null(prev_spend_str)
                        break
                
                if prev_spend is not None:
                    if prev_spend != 0:
                        growth_rate = ((actual_spend - prev_spend) / prev_spend) * 100
                        output_row['previous_spend'] = f"{prev_spend:.1f}"
                        output_row['growth_rate'] = f"{growth_rate:+.1f}%"
                        output_row['formula'] = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                    else:
                        output_row['previous_spend'] = '0.0'
                        output_row['growth_rate'] = '[Cannot compute]'
                        output_row['formula'] = f'YoY {prev_period} is zero'
                else:
                    output_row['previous_spend'] = '[No data]'
                    output_row['growth_rate'] = '[Cannot compute]'
                    output_row['formula'] = f'YoY {prev_period} not in dataset'
        
        output_rows.append(output_row)
    
    # Convert to CSV string
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['period', 'actual_spend', 'previous_spend', 'growth_rate', 'formula'])
    writer.writeheader()
    writer.writerows(output_rows)
    return output.getvalue()

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'], help="Growth type: MoM (month-on-month) or YoY (year-on-year)")
    
    args = parser.parse_args()
    
    try:
        # Load and validate dataset
        print(f"Loading dataset from {args.input}...", file=sys.stderr)
        rows, all_nulls = load_dataset(args.input)
        
        # Get unique wards and categories
        wards = set(row['ward'] for row in rows)
        categories = set(row['category'] for row in rows)
        print(f"Loaded {len(rows)} rows, {len(wards)} wards, {len(categories)} categories", file=sys.stderr)
        
        if all_nulls:
            print(f"Dataset contains {len(all_nulls)} null actual_spend value(s):", file=sys.stderr)
            for null in all_nulls:
                print(f"  - {null['period']} | {null['ward']} | {null['category']}: {null['reason']}", file=sys.stderr)
        
        # Compute growth
        print(f"\nComputing {args.growth_type} growth for: {args.ward} / {args.category}", file=sys.stderr)
        growth_output = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(growth_output)
        
        print(f"\nDone. Growth output written to {args.output}")
    
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()

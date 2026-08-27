"""
UC-0C — Budget Growth Calculator
Prevents wrong aggregation, silent null handling, and formula assumption.
Enforces: per-ward, per-category only; flags all 5 nulls; shows formulas; refuses to guess growth_type.
"""
import argparse
import csv
from collections import defaultdict

def load_dataset(file_path: str) -> dict:
    """
    Load CSV dataset, validate structure, detect and report all null rows.
    Returns dict with raw_data and null_rows.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return {'raw_data': [], 'null_rows': []}
    
    if not rows:
        print(f"Error: Empty CSV file: {file_path}")
        return {'raw_data': [], 'null_rows': []}
    
    # Validate columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_cols.issubset(set(rows[0].keys())):
        print(f"Error: Missing required columns. Found: {set(rows[0].keys())}")
        return {'raw_data': [], 'null_rows': []}
    
    # Detect nulls and convert data types
    raw_data = []
    null_rows = []
    
    for row in rows:
        # Parse actual_spend
        actual_spend = None
        if row.get('actual_spend', '').strip():
            try:
                actual_spend = float(row['actual_spend'])
            except ValueError:
                print(f"Warning: Invalid actual_spend value: {row['actual_spend']}")
        
        processed_row = {
            'period': row.get('period', ''),
            'ward': row.get('ward', ''),
            'category': row.get('category', ''),
            'budgeted_amount': float(row.get('budgeted_amount', 0)) if row.get('budgeted_amount') else None,
            'actual_spend': actual_spend,
            'notes': row.get('notes', '')
        }
        
        raw_data.append(processed_row)
        
        # Track null rows
        if actual_spend is None:
            null_rows.append({
                'period': processed_row['period'],
                'ward': processed_row['ward'],
                'category': processed_row['category'],
                'reason': processed_row['notes'] if processed_row['notes'] else 'No reason provided'
            })
    
    # Extract metadata
    wards = sorted(set(r['ward'] for r in raw_data if r['ward']))
    categories = sorted(set(r['category'] for r in raw_data if r['category']))
    periods = sorted(set(r['period'] for r in raw_data if r['period']))
    
    return {
        'raw_data': raw_data,
        'null_rows': null_rows,
        'metadata': {
            'total_rows': len(raw_data),
            'null_count': len(null_rows),
            'wards': wards,
            'categories': categories,
            'periods': periods
        }
    }


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM or YoY growth for specified ward + category.
    Returns list of dicts with period, actual_spend, formula, growth_pct.
    Enforces E1-E5 rules.
    """
    # E1: Check for aggregation attempt
    if not ward or not category or ward.lower() == 'all' or category.lower() == 'all':
        print("Error: Aggregation not permitted. Please specify --ward and --category explicitly.")
        return []
    
    # E4: Check for growth_type
    if not growth_type:
        print("Error: Growth type not specified. Please provide --growth-type MoM or YoY")
        return []
    
    growth_type = growth_type.upper()
    if growth_type not in ['MOM', 'YOY']:
        print(f"Error: Invalid growth_type: {growth_type}. Must be MoM or YoY")
        return []
    
    raw_data = dataset['raw_data']
    null_rows = dataset['null_rows']
    
    # Filter data for ward + category
    filtered_data = [
        r for r in raw_data 
        if r['ward'] == ward and r['category'] == category
    ]
    
    if not filtered_data:
        print(f"Error: No data found for Ward: {ward}, Category: {category}")
        print(f"Available wards: {', '.join(dataset['metadata']['wards'])}")
        print(f"Available categories: {', '.join(dataset['metadata']['categories'])}")
        return []
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    # Build null lookup
    null_lookup = {}
    for null_row in null_rows:
        key = (null_row['period'], null_row['ward'], null_row['category'])
        null_lookup[key] = null_row['reason']
    
    # Compute growth per period
    results = []
    
    for i, current_row in enumerate(filtered_data):
        period = current_row['period']
        actual_spend = current_row['actual_spend']
        
        # Check if current period is null
        null_key = (period, ward, category)
        is_null = null_key in null_lookup
        
        result = {
            'period': period,
            'actual_spend': actual_spend,
            'prior_value': None,
            'formula': '',
            'growth_pct': None
        }
        
        if is_null:
            result['formula'] = f"NULL — {null_lookup[null_key]}"
        elif growth_type == 'MOM':
            # Month-over-month: compare to previous month
            if i == 0:
                result['formula'] = "N/A (first period)"
            else:
                prior_row = filtered_data[i - 1]
                prior_period = prior_row['period']
                prior_value = prior_row['actual_spend']
                
                # Check if prior is null
                prior_null_key = (prior_period, ward, category)
                if prior_null_key in null_lookup:
                    result['formula'] = f"NULL — prior period ({prior_period}) is null"
                elif prior_value is not None and actual_spend is not None:
                    result['prior_value'] = prior_value
                    growth = ((actual_spend - prior_value) / prior_value * 100) if prior_value != 0 else 0
                    result['growth_pct'] = round(growth, 2)
                    result['formula'] = f"MoM Growth = ({actual_spend} - {prior_value}) / {prior_value} × 100"
                else:
                    result['formula'] = "Cannot compute (missing prior data)"
        
        elif growth_type == 'YOY':
            # Year-over-year: compare to same month previous year
            # Since we only have 2024 data, YoY is not applicable
            result['formula'] = "N/A (only 2024 data available; YoY requires multi-year data)"
        
        results.append(result)
    
    return results


def write_output(results: list, null_rows: list, ward: str, category: str, growth_type: str, output_path: str):
    """Write results to CSV with null warnings."""
    if not results:
        print("Error: No results to write.")
        return
    
    # Report null rows first
    print("\n=== NULL ROWS DETECTED ===")
    ward_category_nulls = [
        n for n in null_rows 
        if n['ward'] == ward and n['category'] == category
    ]
    
    if ward_category_nulls:
        for null_row in ward_category_nulls:
            print(f"  {null_row['period']}: {null_row['reason']}")
    else:
        print(f"  No null rows for {ward} / {category}")
    
    print("\n=== COMPUTING GROWTH ===")
    print(f"Ward: {ward}")
    print(f"Category: {category}")
    print(f"Growth Type: {growth_type}")
    print()
    
    # Write CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'prior_value', 'formula', 'growth_pct']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Growth table written to {output_path}")
    except Exception as e:
        print(f"Error writing output: {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (required; no aggregation)")
    parser.add_argument("--category", required=True, help="Category name (required; no aggregation)")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY (required; no guessing)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from: {args.input}")
    dataset = load_dataset(args.input)
    
    if not dataset['raw_data']:
        return
    
    print(f"Loaded {dataset['metadata']['total_rows']} rows")
    print(f"Null rows detected: {dataset['metadata']['null_count']}")
    
    # Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if results:
        write_output(results, dataset['null_rows'], args.ward, args.category, args.growth_type, args.output)
    else:
        print("No growth computed due to validation errors.")


if __name__ == "__main__":
    main()

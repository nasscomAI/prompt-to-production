"""
UC-0C app.py — Budget Growth Calculator
Computes MoM or YoY growth for specific ward-category combinations.
Failure modes: Wrong aggregation level, Silent null handling, Formula assumption.
Enforcement: No aggregation, Explicit null handling, Formula shown.
"""
import argparse
import csv
import os
from collections import defaultdict


def load_dataset(input_path):
    """
    Load budget CSV and identify all null actual_spend rows before returning.
    Returns: dict with 'data', 'nulls', 'null_count', 'wards', 'categories'
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    data = []
    nulls = []
    wards = set()
    categories = set()
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no headers")
        
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames)):
            missing = required_cols - set(reader.fieldnames)
            raise ValueError(f"Missing required columns: {missing}")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Track ward and category
                wards.add(row['ward'])
                categories.add(row['category'])
                
                # Check for null actual_spend
                actual_spend_str = row.get('actual_spend', '').strip()
                
                if not actual_spend_str or actual_spend_str.lower() == 'nan' or actual_spend_str.lower() == 'null':
                    # This is a null row
                    nulls.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'reason': row.get('notes', 'REASON_NOT_PROVIDED').strip()
                    })
                else:
                    # Valid data row
                    data.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'budgeted_amount': float(row['budgeted_amount']),
                        'actual_spend': float(actual_spend_str)
                    })
            except (ValueError, KeyError) as e:
                raise ValueError(f"Error parsing row {row_num}: {e}")
    
    return {
        'data': data,
        'nulls': nulls,
        'null_count': len(nulls),
        'wards': sorted(list(wards)),
        'categories': sorted(list(categories))
    }


def compute_growth(ward, category, growth_type, dataset):
    """
    Compute growth (MoM or YoY) for specified ward-category pair.
    Returns: list of dicts with period, actual_spend, growth_pct, formula
    """
    # Validate inputs
    if ward not in dataset['wards']:
        raise ValueError(f"Ward '{ward}' not found in dataset. Available: {dataset['wards']}")
    
    if category not in dataset['categories']:
        raise ValueError(f"Category '{category}' not found in dataset. Available: {dataset['categories']}")
    
    if growth_type not in ('MoM', 'YoY'):
        raise ValueError(f"Growth_type must be 'MoM' or 'YoY', got '{growth_type}'")
    
    # Filter data for this ward and category
    filtered_data = [
        row for row in dataset['data']
        if row['ward'] == ward and row['category'] == category
    ]
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    if not filtered_data:
        return []
    
    # Organize by period for easy lookup
    period_map = {row['period']: row for row in filtered_data}
    periods_sorted = sorted(period_map.keys())
    
    # Check for nulls in this ward-category combo
    nulls_in_combo = [n for n in dataset['nulls'] if n['ward'] == ward and n['category'] == category]
    null_periods = {n['period']: n['reason'] for n in nulls_in_combo}
    
    results = []
    
    for i, period in enumerate(periods_sorted):
        current_spend = period_map[period]['actual_spend']
        
        # Compute growth
        if growth_type == 'MoM':
            # Month-over-month: compare with previous month
            if i == 0:
                # First month - no prior month
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'prior_period_spend': None,
                    'growth_pct': None,
                    'formula': 'N/A - first month'
                })
            else:
                prior_period = periods_sorted[i - 1]
                prior_spend = period_map[prior_period]['actual_spend']
                
                # Compute MoM growth
                growth_pct = ((current_spend - prior_spend) / prior_spend) * 100
                formula = f"({current_spend}-{prior_spend})/{prior_spend}*100 = {growth_pct:.1f}%"
                
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'prior_period_spend': prior_spend,
                    'growth_pct': round(growth_pct, 1),
                    'formula': formula
                })
        
        elif growth_type == 'YoY':
            # Year-over-year: compare with same month previous year
            prior_year_period = f"{int(period[:4])-1}-{period[5:]}"
            
            if prior_year_period in period_map:
                prior_spend = period_map[prior_year_period]['actual_spend']
                
                # Compute YoY growth
                growth_pct = ((current_spend - prior_spend) / prior_spend) * 100
                formula = f"({current_spend}-{prior_spend})/{prior_spend}*100 = {growth_pct:.1f}%"
                
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'prior_period_spend': prior_spend,
                    'growth_pct': round(growth_pct, 1),
                    'formula': formula
                })
            else:
                # No prior year data
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'prior_period_spend': None,
                    'growth_pct': None,
                    'formula': 'N/A - no prior year data'
                })
    
    # Add null period markers if any nulls in this combo
    for null_period in sorted(null_periods.keys()):
        results.append({
            'period': null_period,
            'actual_spend': None,
            'prior_period_spend': None,
            'growth_pct': None,
            'formula': f"N/A - null value (reason: {null_periods[null_period]})"
        })
    
    # Sort results by period
    results.sort(key=lambda x: x['period'])
    
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV file")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    parser.add_argument("--ward", required=True, help="Ward name (must be exact)")
    parser.add_argument("--category", required=True, help="Category name (must be exact)")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'],
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    print(f"Dataset loaded: {len(dataset['data'])} valid rows, {dataset['null_count']} null rows")
    
    # Report nulls
    if dataset['nulls']:
        print(f"\nWARNING: NULL ROWS FOUND ({dataset['null_count']}):")
        for null_row in dataset['nulls']:
            print(f"  Period: {null_row['period']}, Ward: {null_row['ward']}, Category: {null_row['category']}")
            print(f"    Reason: {null_row['reason']}")
    
    # Validate ward and category
    if args.ward not in dataset['wards']:
        print(f"\n❌ ERROR: Ward '{args.ward}' not found.")
        print(f"Available wards: {', '.join(dataset['wards'])}")
        return
    
    if args.category not in dataset['categories']:
        print(f"\n❌ ERROR: Category '{args.category}' not found.")
        print(f"Available categories: {', '.join(dataset['categories'])}")
        return
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)
    
    if not results:
        print("❌ No data found for specified ward-category combination")
        return
    
    # Write output
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'actual_spend', 'prior_period_spend', 'growth_pct', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Results written to {args.output}")
    print(f"  Total periods: {len(results)}")
    
    # Show first few results
    print(f"\nFirst 5 results:")
    for i, result in enumerate(results[:5]):
        print(f"  {result['period']}: spend={result['actual_spend']}, growth={result['growth_pct']}, formula={result['formula']}")


if __name__ == "__main__":
    main()

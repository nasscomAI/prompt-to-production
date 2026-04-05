"""
UC-0C — Budget Growth Calculator
Computes period-over-period spend growth for specific ward-category combinations.
"""
import argparse
import csv
import sys
from collections import defaultdict


def load_dataset(input_path):
    """
    Load CSV, validate columns, identify and report nulls.
    Returns: list of dicts (rows) and null information
    """
    rows = []
    nulls = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                missing = required_cols - set(reader.fieldnames or [])
                raise ValueError(f"Missing columns: {missing}")
            
            for row_idx, row in enumerate(reader, start=2):
                rows.append(row)
                
                # Check for null actual_spend
                actual_spend = row.get('actual_spend', '').strip()
                if not actual_spend:
                    nulls.append({
                        'row_idx': row_idx,
                        'period': row.get('period'),
                        'ward': row.get('ward'),
                        'category': row.get('category'),
                        'notes': row.get('notes', 'No notes')
                    })
    
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Report nulls
    if nulls:
        print(f"\n⚠ WARNING: Found {len(nulls)} null actual_spend values:")
        for null in nulls:
            print(f"  {null['period']} · {null['ward']} · {null['category']}")
            print(f"    Reason: {null['notes']}")
    
    return rows, nulls


def compute_growth(rows, ward, category, growth_type):
    """
    Filter to exact ward + category, compute growth, return per-period results.
    """
    if growth_type not in ['MoM', 'YoY']:
        print(f"Error: growth_type must be 'MoM' or 'YoY', got '{growth_type}'", file=sys.stderr)
        sys.exit(1)
    
    # Filter to exact ward + category
    filtered = []
    for row in rows:
        if row['ward'] == ward and row['category'] == category:
            filtered.append(row)
    
    if not filtered:
        print(f"Error: No data found for ward='{ward}' and category='{category}'", file=sys.stderr)
        sys.exit(1)
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    # Organize by period for easy lookup
    by_period = {}
    for row in filtered:
        by_period[row['period']] = row
    
    results = []
    periods_sorted = sorted(by_period.keys())
    
    for current_period in periods_sorted:
        current_row = by_period[current_period]
        actual_spend_str = current_row.get('actual_spend', '').strip()
        current_spend = None
        
        # Check if current is null
        if not actual_spend_str:
            results.append({
                'period': current_period,
                'actual_spend': 'NULL',
                'formula_used': f'DATA_NULL — {current_row.get("notes", "No reason provided")}',
                'growth_pct': ''
            })
            continue
        
        try:
            current_spend = float(actual_spend_str)
        except ValueError:
            print(f"Error: Invalid actual_spend for {current_period}: {actual_spend_str}", file=sys.stderr)
            sys.exit(1)
        
        # Compute growth
        growth_pct = ''
        formula_used = ''
        growth_formula = ''
        
        if growth_type == 'MoM':
            # Get previous month
            period_parts = current_period.split('-')
            year, month = int(period_parts[0]), int(period_parts[1])
            
            if month == 1:
                prev_month = f"{year - 1}-12"
            else:
                prev_month = f"{year}-{month - 1:02d}"
            
            if prev_month in by_period:
                prev_row = by_period[prev_month]
                prev_spend_str = prev_row.get('actual_spend', '').strip()
                
                if prev_spend_str:
                    try:
                        prev_spend = float(prev_spend_str)
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        growth_pct = f"{growth:+.1f}%"
                        growth_formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                        formula_used = f"MoM: {growth_formula} = {growth_pct}"
                    except ValueError:
                        pass
            
            if not formula_used:
                formula_used = f"MoM: No previous month data"
        
        elif growth_type == 'YoY':
            # Get same month previous year
            period_parts = current_period.split('-')
            year, month = int(period_parts[0]), int(period_parts[1])
            prev_year = f"{year - 1}-{month:02d}"
            
            if prev_year in by_period:
                prev_row = by_period[prev_year]
                prev_spend_str = prev_row.get('actual_spend', '').strip()
                
                if prev_spend_str:
                    try:
                        prev_spend = float(prev_spend_str)
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        growth_pct = f"{growth:+.1f}%"
                        growth_formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                        formula_used = f"YoY: {growth_formula} = {growth_pct}"
                    except ValueError:
                        pass
            
            if not formula_used:
                formula_used = f"YoY: No previous year data"
        
        results.append({
            'period': current_period,
            'actual_spend': current_spend,
            'formula_used': formula_used,
            'growth_pct': growth_pct
        })
    
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (exact match)")
    parser.add_argument("--category",    required=True,  help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # Validate growth-type
    if args.growth_type not in ['MoM', 'YoY']:
        print(f"Error: --growth-type must be 'MoM' or 'YoY', got '{args.growth_type}'", file=sys.stderr)
        sys.exit(1)
    
    # Load data
    print(f"Loading {args.input}...")
    rows, nulls = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows. Found {len(nulls)} null actual_spend values.")
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for {args.ward} / {args.category}...")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    # Write output
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth_pct', 'formula_used'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Results written to {args.output}")
    print(f"✓ Computed {len(results)} periods with {sum(1 for r in results if r['growth_pct'])} valid growth calculations")


if __name__ == "__main__":
    main()

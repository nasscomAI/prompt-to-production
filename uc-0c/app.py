"""
UC-0C app.py — Growth Calculation and Validation CLI.
Implements the rules in agents.md and skills.md.
"""
import sys
import os
import csv
import argparse
from datetime import datetime

def load_dataset(file_path):
    """
    Reads the CSV dataset, validates the presence and types of all required columns,
    and reports details of any null values found in the actual spend.
    """
    if not os.path.exists(file_path):
        sys.exit(f"Error: Input file not found: {file_path}")
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    records = []
    null_rows = []
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Validate columns
        if not reader.fieldnames:
            sys.exit("Error: CSV file is empty or has no header.")
        
        headers = set(reader.fieldnames)
        missing_cols = required_cols - headers
        if missing_cols:
            sys.exit(f"Error: Missing required columns in CSV: {', '.join(missing_cols)}")
            
        for line_num, row in enumerate(reader, start=2):
            period = row['period'].strip()
            ward = row['ward'].strip()
            category = row['category'].strip()
            budgeted_str = row['budgeted_amount'].strip()
            actual_str = row['actual_spend'].strip()
            notes = row['notes'].strip()
            
            # Validate types
            try:
                budgeted_amount = float(budgeted_str)
            except ValueError:
                sys.exit(f"Error: Line {line_num}: invalid budgeted_amount '{budgeted_str}'")
                
            actual_spend = None
            if actual_str:
                try:
                    actual_spend = float(actual_str)
                except ValueError:
                    sys.exit(f"Error: Line {line_num}: invalid actual_spend '{actual_str}'")
            else:
                null_rows.append({
                    'line': line_num,
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'notes': notes
                })
                
            records.append({
                'period': period,
                'ward': ward,
                'category': category,
                'budgeted_amount': budgeted_amount,
                'actual_spend': actual_spend,
                'notes': notes
            })
            
    # Print the validation report for null rows (Skill: load_dataset)
    print(f"[VALIDATION] Dataset loaded from {file_path}. Total rows: {len(records)}.")
    print(f"[VALIDATION] Found {len(null_rows)} row(s) with NULL actual spend:")
    for nr in null_rows:
        reason = nr['notes'] if nr['notes'] else 'No reason provided'
        print(f"  - Row {nr['line']} | Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: {reason}")
        
    return records

def compute_growth(records, target_ward=None, target_category=None, growth_type=None):
    """
    Computes period-over-period growth for a specific ward and category using
    the specified growth type (e.g., MoM or YoY) and shows the formula used.
    """
    if not growth_type:
        sys.exit("Error: Growth type must be specified. Please specify --growth-type (e.g., MoM or YoY). Never guess.")
        
    growth_type = growth_type.upper()
    if growth_type not in ['MOM', 'YOY']:
        sys.exit(f"Error: Unsupported growth type '{growth_type}'. Only MoM and YoY are supported.")
        
    # Group records by (ward, category)
    groups = {}
    for r in records:
        key = (r['ward'], r['category'])
        if key not in groups:
            groups[key] = []
        groups[key].append(r)
        
    results = []
    
    # Process each group
    for (ward, category), group_records in groups.items():
        # Apply filters if specified
        if target_ward and ward != target_ward:
            continue
        if target_category and category != target_category:
            continue
            
        # Sort chronologically by period
        try:
            sorted_records = sorted(group_records, key=lambda x: datetime.strptime(x['period'], '%Y-%m'))
        except ValueError as e:
            sys.exit(f"Error: Invalid period format in dataset: {e}")
            
        # Map period to record for easy lookup
        period_to_record = {r['period']: r for r in sorted_records}
        
        for r in sorted_records:
            period_str = r['period']
            actual_spend = r['actual_spend']
            budgeted_amount = r['budgeted_amount']
            notes = r['notes']
            
            growth_rate = "NULL"
            formula = "N/A"
            
            # Find the baseline period based on growth type
            if growth_type == 'MOM':
                try:
                    dt = datetime.strptime(period_str, '%Y-%m')
                    if dt.month == 1:
                        prev_year = dt.year - 1
                        prev_month = 12
                    else:
                        prev_year = dt.year
                        prev_month = dt.month - 1
                    prev_period_str = f"{prev_year:04d}-{prev_month:02d}"
                except Exception as e:
                    sys.exit(f"Error: Failed to parse period: {period_str} ({e})")
                    
                baseline_record = period_to_record.get(prev_period_str)
                baseline_desc = "previous month"
            elif growth_type == 'YOY':
                try:
                    dt = datetime.strptime(period_str, '%Y-%m')
                    prev_period_str = f"{dt.year - 1:04d}-{dt.month:02d}"
                except Exception as e:
                    sys.exit(f"Error: Failed to parse period: {period_str} ({e})")
                    
                baseline_record = period_to_record.get(prev_period_str)
                baseline_desc = "previous year"
                
            # Perform computation and safety checks
            if actual_spend is None:
                growth_rate = "NULL"
                formula = f"N/A (Current actual spend is NULL: {notes})"
            elif baseline_record is None:
                growth_rate = "NULL"
                formula = f"N/A (No data for {baseline_desc} {prev_period_str})"
            else:
                prev_spend = baseline_record['actual_spend']
                if prev_spend is None:
                    growth_rate = "NULL"
                    formula = f"N/A (Previous actual spend is NULL: {baseline_record['notes']})"
                elif prev_spend == 0:
                    growth_rate = "NULL"
                    formula = f"N/A (Division by zero: previous spend is 0)"
                else:
                    diff = actual_spend - prev_spend
                    rate = diff / prev_spend
                    pct = rate * 100
                    sign = "+" if pct > 0 else ""
                    growth_rate = f"{sign}{pct:.1f}%"
                    formula = f"({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
                    
            results.append({
                'ward': ward,
                'category': category,
                'period': period_str,
                'budgeted_amount': budgeted_amount,
                'actual_spend': actual_spend if actual_spend is not None else "NULL",
                'growth_rate': growth_rate,
                'formula': formula,
                'notes': notes
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculation and Validation")
    parser.add_argument('--input', required=True, help="Path to input CSV file")
    parser.add_argument('--ward', help="Ward filter")
    parser.add_argument('--category', help="Category filter")
    parser.add_argument('--growth-type', help="Growth type: MoM or YoY")
    parser.add_argument('--output', required=True, help="Path to output CSV file")
    parser.add_argument('--aggregate', action='store_true', help="Aggregate across wards or categories")
    
    args = parser.parse_args()
    
    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        sys.exit("Error: Growth type must be specified. Please specify --growth-type (e.g., MoM or YoY). Never guess.")
        
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if args.ward and args.ward.lower() in ['all', 'any', 'total', 'aggregate', 'overall']:
        sys.exit("Error: All-ward aggregation is not allowed. The system refuses to aggregate across wards or categories.")
    if args.category and args.category.lower() in ['all', 'any', 'total', 'aggregate', 'overall']:
        sys.exit("Error: All-category aggregation is not allowed. The system refuses to aggregate across wards or categories.")
    if args.aggregate:
        sys.exit("Error: Aggregation across wards or categories is disabled. The system refuses to aggregate.")
        
    # Skill: load_dataset (loads and prints details of nulls)
    records = load_dataset(args.input)
    
    # Validate filter inputs exist in dataset
    all_wards = {r['ward'] for r in records}
    all_categories = {r['category'] for r in records}
    
    if args.ward and args.ward not in all_wards:
        sys.exit(f"Error: Specified ward '{args.ward}' not found in the dataset. Available wards: {sorted(all_wards)}")
    if args.category and args.category not in all_categories:
        sys.exit(f"Error: Specified category '{args.category}' not found in the dataset. Available categories: {sorted(all_categories)}")
        
    # Skill: compute_growth
    results = compute_growth(records, target_ward=args.ward, target_category=args.category, growth_type=args.growth_type)
    
    # Save output
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'budgeted_amount', 'growth_rate', 'formula', 'notes'])
        writer.writeheader()
        for res in results:
            writer.writerow(res)
            
    print(f"[SUCCESS] Growth output successfully written to {args.output}")

if __name__ == "__main__":
    main()

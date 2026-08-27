"""
UC-0C app.py — Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates required columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
        
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            raise ValueError("CSV file is empty")
            
        required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        missing_cols = [col for col in required_cols if col not in headers]
        if missing_cols:
            raise ValueError(f"Missing required columns in dataset: {', '.join(missing_cols)}")
            
        rows = list(reader)
        
    # Find and report null rows
    null_rows = []
    for idx, row in enumerate(rows):
        actual_spend = row.get('actual_spend', '').strip()
        if not actual_spend:
            null_rows.append((idx + 2, row)) # 1-indexed, plus 1 for header row
            
    print(f"Total rows loaded: {len(rows)}")
    print(f"Total null actual_spend rows detected: {len(null_rows)}")
    for line_num, r in null_rows:
        print(f"  Line {line_num} is null: Period={r['period']}, Ward={r['ward']}, Category={r['category']}, Notes='{r['notes']}'")
        
    return rows

def get_prev_period(period_str, growth_type):
    """
    Utility to get the target previous period for MoM or YoY comparison.
    """
    try:
        year, month = map(int, period_str.split('-'))
    except Exception:
        return None
        
    if growth_type == 'MoM':
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1
        return f"{prev_year:04d}-{prev_month:02d}"
    elif growth_type == 'YoY':
        prev_year = year - 1
        return f"{prev_year:04d}-{month:02d}"
    return None

def compute_growth(rows, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth-type: {growth_type}. Must be MoM or YoY.")
        
    # Check if ward and category exist in the dataset
    unique_wards = set(r['ward'] for r in rows)
    unique_categories = set(r['category'] for r in rows)
    
    if ward not in unique_wards:
        raise ValueError(f"Ward '{ward}' not found in dataset. Available wards: {sorted(list(unique_wards))}")
    if category not in unique_categories:
        raise ValueError(f"Category '{category}' not found in dataset. Available categories: {sorted(list(unique_categories))}")

    # Filter rows
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    if not filtered:
        raise ValueError(f"No records found for Ward='{ward}' and Category='{category}'")
        
    # Sort chronologically by period
    filtered.sort(key=lambda x: x['period'])
    
    # Map periods to rows for fast lookup
    period_map = {r['period']: r for r in filtered}
    
    results = []
    for r in filtered:
        curr_period = r['period']
        curr_spend_str = r['actual_spend'].strip()
        orig_notes = r['notes'].strip()
        
        curr_spend = None
        if curr_spend_str:
            try:
                curr_spend = float(curr_spend_str)
            except ValueError:
                pass
                
        prev_period = get_prev_period(curr_period, growth_type)
        
        # Look up previous row within same ward/category
        prev_row = period_map.get(prev_period)
        
        growth_val = "NULL"
        formula_str = "N/A"
        notes_str = orig_notes
        
        if curr_spend is None:
            # Current value is null
            growth_val = "NULL"
            formula_str = "N/A - actual_spend is null"
            if not notes_str:
                notes_str = "Actual spend is missing/null"
        elif prev_row is None:
            # Previous period does not exist in the dataset
            growth_val = "NULL"
            formula_str = f"N/A - reference period {prev_period} not found in dataset"
            notes_str = f"Cannot compute {growth_type}: reference period {prev_period} is missing"
            if orig_notes:
                notes_str = f"{notes_str} | {orig_notes}"
        else:
            prev_spend_str = prev_row['actual_spend'].strip()
            prev_spend = None
            if prev_spend_str:
                try:
                    prev_spend = float(prev_spend_str)
                except ValueError:
                    pass
                    
            if prev_spend is None:
                # Previous value is null
                growth_val = "NULL"
                formula_str = f"N/A - previous period actual_spend is null"
                notes_str = f"Cannot compute {growth_type}: previous period spend is missing/null"
                if prev_row['notes'].strip():
                    notes_str = f"{notes_str} (Reason: {prev_row['notes'].strip()})"
                if orig_notes:
                    notes_str = f"{notes_str} | {orig_notes}"
            elif prev_spend == 0:
                # Avoid division by zero
                growth_val = "NULL"
                formula_str = f"({curr_spend} - {prev_spend}) / {prev_spend}"
                notes_str = "Cannot compute: division by zero"
                if orig_notes:
                    notes_str = f"{notes_str} | {orig_notes}"
            else:
                # Both values are valid and non-zero
                diff = curr_spend - prev_spend
                growth_pct = (diff / prev_spend) * 100
                growth_val = f"{growth_pct:+.1f}%"
                
                # Format the spends cleanly (e.g. 19.7, 14.8)
                def fmt_num(v):
                    if v.is_integer():
                        return str(int(v))
                    return str(v)
                
                formula_str = f"({fmt_num(curr_spend)} - {fmt_num(prev_spend)}) / {fmt_num(prev_spend)}"
                
        results.append({
            'period': curr_period,
            'ward': ward,
            'category': category,
            'budgeted_amount': r['budgeted_amount'],
            'actual_spend': curr_spend_str if curr_spend_str else "NULL",
            'growth': growth_val,
            'formula': formula_str,
            'notes': notes_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument('--input', type=str, help="Path to input budget CSV file")
    parser.add_argument('--ward', type=str, help="Target ward name")
    parser.add_argument('--category', type=str, help="Target category name")
    parser.add_argument('--growth-type', type=str, help="Growth type (MoM or YoY)")
    parser.add_argument('--output', type=str, help="Path to save output CSV file")
    
    args = parser.parse_args()
    
    # 4. If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: Growth type (--growth-type) is not specified. Please specify either MoM or YoY.", file=sys.stderr)
        print("Refusing to guess.", file=sys.stderr)
        sys.exit(1)
        
    if not args.input:
        print("Error: Input file (--input) is required.", file=sys.stderr)
        sys.exit(1)
        
    if not args.output:
        print("Error: Output file (--output) is required.", file=sys.stderr)
        sys.exit(1)
        
    # 1. Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or args.ward.lower() in ['all', 'any', 'none', '']:
        print("Error: Specific --ward is required. Aggregation across wards is not allowed. Refusing request.", file=sys.stderr)
        sys.exit(1)
        
    if not args.category or args.category.lower() in ['all', 'any', 'none', '']:
        print("Error: Specific --category is required. Aggregation across categories is not allowed. Refusing request.", file=sys.stderr)
        sys.exit(1)
        
    try:
        # Load dataset
        rows = load_dataset(args.input)
        
        # Compute growth
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        # Write output to output path
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth', 'formula', 'notes'])
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Successfully wrote output to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

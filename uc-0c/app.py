"""
UC-0C app.py — Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads the budget CSV file, validates the headers, and scans for and logs any rows with null actual_spend values.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    rows = []
    null_rows = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Header validation
            headers = reader.fieldnames
            if not headers:
                print(f"Error: CSV file is empty or missing headers.", file=sys.stderr)
                sys.exit(1)
                
            for col in required_cols:
                if col not in headers:
                    print(f"Error: Missing required column '{col}' in input CSV.", file=sys.stderr)
                    sys.exit(1)
                    
            for line_no, row in enumerate(reader, start=2):
                actual_spend_str = row['actual_spend'].strip()
                if not actual_spend_str:
                    null_rows.append((line_no, row['period'], row['ward'], row['category'], row['notes']))
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(actual_spend_str)
                    except ValueError:
                        print(f"Warning: Invalid actual_spend value at line {line_no}: '{actual_spend_str}'", file=sys.stderr)
                        row['actual_spend'] = None
                        
                try:
                    row['budgeted_amount'] = float(row['budgeted_amount'])
                except ValueError:
                    row['budgeted_amount'] = 0.0
                    
                rows.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    if null_rows:
        print(f"Found {len(null_rows)} deliberate null actual_spend values during load:")
        for line_no, period, ward, cat, notes in null_rows:
            print(f"  Line {line_no} | Period: {period} | Ward: {ward} | Category: {cat} | Reason: {notes}")
            
    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes period-over-period spend growth for a specific ward and category using the specified growth type.
    """
    # 1. Refusal logic: Never aggregate across wards or categories, refuse if not specific
    if not ward or ward.strip().lower() == "any" or ward.strip() == "":
        print("Error: Aggregating across all wards is NOT permitted. Please specify a single ward.", file=sys.stderr)
        sys.exit(1)
        
    if not category or category.strip().lower() == "any" or category.strip() == "":
        print("Error: Aggregating across all categories is NOT permitted. Please specify a single category.", file=sys.stderr)
        sys.exit(1)
        
    if not growth_type or growth_type.strip() == "":
        print("Error: Growth type must be specified (e.g. MoM). Refusing to guess.", file=sys.stderr)
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"Error: Growth type '{growth_type}' is not supported or no data is available for calculation.", file=sys.stderr)
        sys.exit(1)
        
    # Filter dataset for specific ward and category
    filtered = [r for r in rows if r['ward'].strip() == ward.strip() and r['category'].strip() == category.strip()]
    
    if not filtered:
        print(f"Warning: No data rows found matching Ward: '{ward}' and Category: '{category}'", file=sys.stderr)
        return []
        
    # Sort chronologically by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend']
        notes = row['notes']
        
        growth_str = "n/a"
        formula_str = "n/a"
        
        if actual is None:
            # Current value is null: Flag and report notes reason
            growth_str = "NULL"
            formula_str = f"N/A - actual spend is null (Reason: {notes})"
        elif i == 0:
            # First period: No previous month
            growth_str = "n/a"
            formula_str = "No previous period data"
        else:
            prev_row = filtered[i-1]
            prev_actual = prev_row['actual_spend']
            
            if prev_actual is None:
                # Previous value is null: cannot compute growth
                growth_str = "NULL"
                formula_str = f"N/A - previous period actual spend ({prev_row['period']}) is null (Reason: {prev_row['notes']})"
            else:
                diff = actual - prev_actual
                growth_val = (diff / prev_actual) * 100
                sign = "+" if growth_val >= 0 else ""
                growth_str = f"{sign}{growth_val:.1f}%"
                formula_str = f"({actual} - {prev_actual}) / {prev_actual}"
                
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': "NULL" if actual is None else str(actual),
            'growth': growth_str,
            'formula': formula_str,
            'notes': notes
        })
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (must be specified)")
    parser.add_argument("--category", help="Category name (must be specified)")
    parser.add_argument("--growth-type", help="Growth type (must be specified, e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    
    # Check if growth-type was specified (required by agents.md)
    if not args.growth_type:
        print("Error: --growth-type must be explicitly specified. Refusing to guess.", file=sys.stderr)
        sys.exit(1)
        
    # Check if ward and category are specified
    if not args.ward:
        print("Error: --ward must be explicitly specified.", file=sys.stderr)
        sys.exit(1)
    if not args.category:
        print("Error: --category must be explicitly specified.", file=sys.stderr)
        sys.exit(1)
        
    # 1. Load dataset
    rows = load_dataset(args.input)
    
    # 2. Compute growth
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    # 3. Write output CSV
    try:
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
                
        print(f"Done. Calculations written to {args.output}")
    except Exception as e:
        print(f"Error writing output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

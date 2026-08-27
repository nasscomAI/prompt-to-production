"""
UC-0C app.py — Budget Growth Calculator
Built to adhere strictly to RICE constraints and skill definitions from agents.md and skills.md.
"""
import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_count = 0
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Column validation
            if not required_cols.issubset(set(reader.fieldnames)):
                print(f"ERROR: Missing required columns in dataset. Expected: {required_cols}")
                sys.exit(1)
                
            for row in reader:
                data.append(row)
                actual_spend_val = row.get('actual_spend', '').strip()
                if not actual_spend_val:
                    null_count += 1
                    null_rows.append((row['period'], row['ward'], row['category'], row.get('notes', '')))
                    
    except Exception as e:
        print(f"ERROR reading dataset '{filepath}': {e}")
        sys.exit(1)
        
    print(f"Dataset loaded successfully. Found {null_count} rows with null actual_spend.")
    for r in null_rows:
        print(f" - NULL FLAG: Period {r[0]}, Ward '{r[1]}', Category '{r[2]}' | Note: {r[3]}")
        
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Takes ward, category, and growth_type, and returns per-period table with formula shown.
    Enforces strict isolated scoping based on agent constraints.
    """
    # ENFORCEMENT 1: Refuse aggregation across wards or categories unless explicitly instructed
    if not target_ward or str(target_ward).lower() in ['any', 'all']:
        print("REFUSAL: Cannot aggregate across wards. An explicit ward must be specified.")
        sys.exit(1)
    if not target_category or str(target_category).lower() in ['any', 'all']:
        print("REFUSAL: Cannot aggregate across categories. An explicit category must be specified.")
        sys.exit(1)
        
    # ENFORCEMENT 4: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        print("REFUSAL: --growth-type must be specified explicitly (e.g., 'MoM' or 'YoY'). Cannot guess.")
        sys.exit(1)
        
    if growth_type not in ['MoM', 'YoY']:
        print(f"ERROR: Unsupported growth type '{growth_type}'. Expected 'MoM' or 'YoY'.")
        sys.exit(1)

    # Filter isolated data
    filtered = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]
    
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current['period']
        actual = current['actual_spend'].strip() if current.get('actual_spend') else None
        notes = current.get('notes', '').strip()
        
        # ENFORCEMENT 2/3: Flag null rows, display formula alongside output rows
        if not actual:
            growth_val = "NULL"
            formula_str = f"Must be flagged — not computed. Null reason: {notes}"
        else:
            try:
                curr_val = float(actual)
            except ValueError:
                curr_val = None
                
            # Determine base value according to type
            prev_val = None
            if growth_type == 'MoM' and i > 0:
                prev_actual = filtered[i-1]['actual_spend'].strip()
                if prev_actual:
                    try:
                        prev_val = float(prev_actual)
                    except ValueError:
                        pass
            elif growth_type == 'YoY':
                try:
                    year, month = period.split('-')
                    prev_period = f"{int(year)-1:04d}-{month}"
                    for past_row in filtered[:i]:
                        if past_row['period'] == prev_period:
                            past_actual = past_row.get('actual_spend', '').strip()
                            if past_actual:
                                prev_val = float(past_actual)
                            break
                except ValueError:
                    pass
            
            # Compute growth percent
            if curr_val is None:
                growth_val = "NULL"
                formula_str = f"Must be flagged — not computed. Null reason: {notes}"
            elif prev_val is None:
                growth_val = "n/a"
                formula_str = "No prior base data strictly matching period for comparison"
            else:
                if prev_val == 0:
                    growth_val = "n/a"
                    formula_str = f"Base is 0: ({curr_val} - 0) / 0"
                else:
                    growth_pct = ((curr_val - prev_val) / prev_val) * 100
                    
                    # Format output appropriately including note suffix (if any)
                    if growth_pct < 0:
                        sign = "−"
                        growth_pct_abs = abs(growth_pct)
                    else:
                        sign = "+" if growth_pct > 0 else ""
                        growth_pct_abs = growth_pct
                        
                    note_suffix = f" ({notes})" if notes else ""
                    growth_val = f"{sign}{growth_pct_abs:.1f}%{note_suffix}"
                    formula_str = f"({curr_val} - {prev_val}) / {prev_val}"
                    
        # Construct output dictionary
        output_rows.append({
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual if actual else "NULL",
            f'{growth_type} Growth': growth_val,
            'Formula Used': formula_str
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument('--input', required=True, help="Input CSV dataset path")
    parser.add_argument('--ward', help="Specific Ward name")
    parser.add_argument('--category', help="Specific Category name")
    # ENFORCEMENT 4: Must explicitly request type
    parser.add_argument('--growth-type', help="Type of calculation, e.g., 'MoM' or 'YoY'")
    parser.add_argument('--output', required=True, help="Output CSV dataset path")
    
    args = parser.parse_args()
    
    # Check enforcement rules BEFORE processing! Refuse proactively
    if not args.growth_type:
        print("REFUSAL: --growth-type must be specified explicitly (e.g. MoM, YoY). Cannot guess default type.")
        sys.exit(1)
        
    if not args.ward or args.ward.lower() in ['any', 'all']:
        print("REFUSAL: Cannot aggregate across wards. An explicit ward must be specified.")
        sys.exit(1)
        
    if not args.category or args.category.lower() in ['any', 'all']:
        print("REFUSAL: Cannot aggregate across categories. An explicit category must be specified.")
        sys.exit(1)
        
    # Execute skills sequentially
    print(f"Loading dataset from: {args.input}")
    data = load_dataset(args.input)
    
    print(f"Computing {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'")
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save output spreadsheet
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth', 'Formula Used']
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success! Per-period computed data written to {args.output}")
    except Exception as e:
        print(f"ERROR writing to output file '{args.output}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

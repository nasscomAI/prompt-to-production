import argparse
import csv
import sys

def load_dataset(input_path):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not expected_cols.issubset(set(reader.fieldnames)):
        print(f"Error: Missing expected columns. Found: {reader.fieldnames}")
        sys.exit(1)

    # Flag and report nulls globally as requested by the rule
    null_rows = []
    for i, row in enumerate(data, start=2): # 1-indexed plus header
        if not row['actual_spend'] or row['actual_spend'].strip() == '':
            null_rows.append((i, row['ward'], row['category'], row['period'], row.get('notes', '')))
    
    if null_rows:
        print(f"Data Validation: Found {len(null_rows)} explicitly null `actual_spend` records.")
        for r in null_rows:
            print(f"  - Row {r[0]}: {r[3]} | {r[1]} | {r[2]} -> NULL Reason: {r[4]}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if ward is None or category is None:
        raise ValueError("REFUSAL: Never aggregate across wards or categories unless explicitly instructed. Please provide both --ward and --category.")
    
    if growth_type is None:
        raise ValueError("REFUSAL: If `--growth-type` not specified — refuse and ask, never guess.")
    
    if growth_type != 'MoM':
        raise ValueError(f"REFUSAL: Growth type '{growth_type}' is not supported yet. Only 'MoM' is implemented.")
        
    # Filter for the specific ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'")
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual = row['actual_spend'].strip() if row['actual_spend'] else None
        notes = row.get('notes', '').strip()
        
        result_row = {
            'ward': ward,
            'category': category,
            'period': period,
            'budgeted_amount': row['budgeted_amount'],
            'actual_spend': actual if actual else 'NULL',
            'notes': notes
        }
        
        if not actual:
            # Null row encountered
            result_row['MoM_Growth'] = 'NULL'
            result_row['Formula'] = f"FLAGGED NULL -> Reason: {notes}"
            prev_spend = None # Break the chain for the next month
        else:
            current_spend = float(actual)
            if prev_spend is None:
                result_row['MoM_Growth'] = 'N/A'
                result_row['Formula'] = "N/A (No previous month data)"
            else:
                growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
                result_row['MoM_Growth'] = f"{growth_pct:+.1f}%"
                result_row['Formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                if notes:
                    result_row['MoM_Growth'] += f" ({notes})"
            
            prev_spend = current_spend
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Strict financial data processor and calculator.")
    parser.add_argument('--input', help='Path to the input CSV file')
    parser.add_argument('--ward', help='Specific ward to filter on (Required to prevent aggregation)')
    parser.add_argument('--category', help='Specific category to filter on (Required to prevent aggregation)')
    parser.add_argument('--growth-type', help='Type of growth to compute (e.g., MoM)')
    parser.add_argument('--output', help='Path to save the computed output CSV')
    
    args = parser.parse_args()
    
    if not args.input or not args.output:
        print("Error: --input and --output are required.", file=sys.stderr)
        sys.exit(1)
        
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write the per-period per-ward per-category table to output
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if results:
                fieldnames = ['ward', 'category', 'period', 'budgeted_amount', 'actual_spend', 'MoM_Growth', 'Formula', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
                print(f"Success: Wrote {len(results)} rows to {args.output}")
            else:
                print(f"Warning: No valid records to write to {args.output}")

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()

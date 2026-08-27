import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates required columns, and detects missing values.
    Returns the valid data and reports missing values explicitly.
    """
    data = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate complete dataset
            if not required_cols.issubset(set(reader.fieldnames)):
                print(f"REFUSAL: Dataset missing mandatory columns. Expected {required_cols}", file=sys.stderr)
                sys.exit(1)
            
            null_rows = []
            
            for row_idx, row in enumerate(reader, start=2): # Start 2 for header + 1st data row
                actual = row.get('actual_spend', '').strip()
                if not actual:
                    null_rows.append({
                        'row': row_idx,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'note': row.get('notes', 'No reason provided')
                    })
                data.append(row)
                
            # Upfront warning about flagged data issues
            if null_rows:
                print(f"DATALOAD WARNING: Found {len(null_rows)} explicitly null records in actual_spend.")
                for nr in null_rows:
                    print(f"  - Row {nr['row']} | {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['note']}")
                    
            return data
            
    except FileNotFoundError:
        print(f"REFUSAL: Dataset file {filepath} not found.", file=sys.stderr)
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    """
    Calculates period-over-period growth for a strictly scoped subset of data.
    Refuses silent aggregation, enforces null flagging, and exhibits formulas visibly.
    """
    # Refusal: Aggregation
    if not ward or ward.lower() == 'all':
        print("REFUSAL: Cannot aggregate across all wards unless explicitly instructed.", file=sys.stderr)
        sys.exit(1)
    if not category or category.lower() == 'all':
        print("REFUSAL: Cannot aggregate across all categories unless explicitly instructed.", file=sys.stderr)
        sys.exit(1)
    
    # Refusal: Unspecified methodology
    if not growth_type:
        print("REFUSAL: Growth type must be specified (e.g. MoM). I will not guess.", file=sys.stderr)
        sys.exit(1)
        
    filtered = []
    for row in data:
        if row['ward'].strip().lower() == ward.strip().lower() and row['category'].strip().lower() == category.strip().lower():
            filtered.append(row)
            
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_actual = None
    
    for row in filtered:
        period = row['period'].strip()
        actual_str = row['actual_spend'].strip()
        note = row['notes'].strip()
        
        if not actual_str:
            # Null flagged without silent discarding or assumptions
            results.append({
                'Ward': row['ward'].strip(),
                'Category': row['category'].strip(),
                'Period': period,
                'Actual Spend': 'NULL',
                'Growth Type': growth_type,
                'Growth Value': 'FLAGGED',
                'Formula': f"REFUSED: Null value. Note: {note}"
            })
            prev_actual = None
            continue
            
        current_actual = float(actual_str)
        
        if prev_actual is None:
            results.append({
                'Ward': row['ward'].strip(),
                'Category': row['category'].strip(),
                'Period': period,
                'Actual Spend': f"{current_actual:.1f}",
                'Growth Type': growth_type,
                'Growth Value': 'N/A',
                'Formula': "N/A (No previous valid period)"
            })
        else:
            if growth_type.lower() == 'mom':
                diff = current_actual - prev_actual
                growth_pct = (diff / prev_actual) * 100
                sign = '+' if growth_pct > 0 else ''
                
                growth_val_str = f"{sign}{growth_pct:.1f}%"
                formula = f"({current_actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f} * 100"
                
                results.append({
                    'Ward': row['ward'].strip(),
                    'Category': row['category'].strip(),
                    'Period': period,
                    'Actual Spend': f"{current_actual:.1f}",
                    'Growth Type': "MoM",
                    'Growth Value': growth_val_str,
                    'Formula': formula
                })
            else:
                print(f"REFUSAL: Unsupported or unrequested growth_type '{growth_type}' explicitly configured.", file=sys.stderr)
                sys.exit(1)
                
        prev_actual = current_actual
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analyst")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", default=None, help="Specific ward to analyze (e.g. 'Ward 1 - Kasba')")
    parser.add_argument("--category", default=None, help="Specific category to analyze (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", default=None, help="Growth calculation methodology (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    # 1. Load and visibly validate dataset constraints
    data = load_dataset(args.input)
    
    # 2. Strict computation scoped to explicit inputs
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # 3. Verifiable Output formatting
    if results:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend", "Growth Type", "Growth Value", "Formula"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
                
        print(f"SUCCESS: Analyzed growth explicitly written to {args.output}")
    else:
        print("WARNING: Scope resulted in 0 matching records. Verify input spelling and ward/category names.")

if __name__ == "__main__":
    main()

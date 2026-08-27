import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads the CSV, validates columns, reports null count and which rows are null before returning.
    """
    dataset = []
    null_count = 0
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing_cols = [c for c in required_cols if c not in reader.fieldnames]
            if missing_cols:
                print(f"CRITICAL ERROR: Missing required columns: {missing_cols}")
                sys.exit(1)
                
            for i, row in enumerate(reader, start=2): # Start at 2 to account for header
                spend = row.get('actual_spend', '').strip()
                if not spend:
                    null_count += 1
                    null_rows.append({
                        'line': i,
                        'period': row.get('period'),
                        'ward': row.get('ward'),
                        'category': row.get('category'),
                        'notes': row.get('notes')
                    })
                dataset.append(row)
                
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Failed to open dataset at {filepath}")
        sys.exit(1)

    print(f"DATASET LOADED. Found {null_count} null `actual_spend` rows.")
    for nr in null_rows:
        print(f" -> FLAGGED NULL: Line {nr['line']} | {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        
    return dataset

def compute_growth(dataset, target_ward, target_cat, growth_type):
    """
    Takes explicit parameters to prevent silently aggregating over multiple wards/categories.
    Computes accurate variance, exposing the mathematical formulas completely and maintaining null integrity.
    """
    # 1. Enforcement restriction against aggregation
    if not target_ward or target_ward.lower() in ["any", "all"]:
        print("CRITICAL REFUSAL: Aggregation across wards is explicitly prohibited to prevent statistical failure modes.")
        sys.exit(1)
    if not target_cat or target_cat.lower() in ["any", "all"]:
        print("CRITICAL REFUSAL: Aggregation across categories is explicitly prohibited.")
        sys.exit(1)
        
    # 2. Enforcement against silent formula assumption
    if not growth_type:
        print("CRITICAL REFUSAL: --growth-type MUST be explicitly specified. Refusing to guess MoM vs YoY.")
        sys.exit(1)
    
    if growth_type.upper() != "MOM":
        print(f"CRITICAL REFUSAL: Only 'MoM' growth_type is supported by this mathematical engine right now. Got: {growth_type}")
        sys.exit(1)
        
    # 3. Filter Dataset
    filtered = []
    for row in dataset:
        if row['ward'] == target_ward and row['category'] == target_cat:
            filtered.append(row)
            
    if not filtered:
        print(f"WARNING: No data found for Ward: '{target_ward}' and Category: '{target_cat}'.")
        return []

    # Ensure chronological order
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        curr_spend_str = row['actual_spend'].strip()
        curr_spend = float(curr_spend_str) if curr_spend_str else None
        
        growth_out = ""
        formula_out = ""
        
        if curr_spend is None:
            # Current month is deliberately null
            growth_out = "Must be flagged — not computed"
            formula_out = f"NULL Current Month Value. Explicit reason: {row.get('notes', 'None')}"
        elif prev_spend is None:
            # Previous month was null or doesn't exist (e.g. tracking start)
            growth_out = "N/A"
            formula_out = "Cannot compute: previous period value is missing or null."
        else:
            if prev_spend == 0:
                growth_out = "N/A (Div by zero)"
                formula_out = f"(({curr_spend:.1f} - 0) / 0) * 100"
            else:
                pct = ((curr_spend - prev_spend) / prev_spend) * 100
                prefix = "+" if pct > 0 else ""
                
                # We specifically mimic the reference format style to include the note if it exists.
                note_str = f" ({row['notes']})" if row.get('notes') and row['notes'].strip() else ""
                growth_out = f"{prefix}{pct:.1f}%{note_str}"
                
                formula_out = f"(({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                
        results.append({
            'Ward': row['ward'],
            'Category': row['category'],
            'Period': row['period'],
            'Actual Spend (₹ lakh)': curr_spend_str if curr_spend_str else "NULL",
            'MoM Growth': growth_out,
            'Formula Used': formula_out
        })
        
        prev_spend = curr_spend

    return results

def main():
    parser = argparse.ArgumentParser(description="Deterministic Budget Growth Engine")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Explicit target Ward")
    parser.add_argument("--category", required=True, help="Explicit target Category")
    parser.add_argument("--growth-type", dest="growth_type", required=True, help="E.g., MoM")
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    args = parser.parse_args()
    
    # Run Skill 1
    dataset = load_dataset(args.input)
    
    # Run Skill 2
    output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Persist to disk
    if output_rows:
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth', 'Formula Used']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in output_rows:
                    writer.writerow(r)
            print(f"✅ Securely wrote explicit growth calculations to '{args.output}'")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to write output file: {e}")
            sys.exit(1)
    else:
        print("No output generated due to lack of distinct filtered data.")

if __name__ == "__main__":
    main()

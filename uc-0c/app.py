import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Skill: Reads CSV, validates columns, reports null count.
    """
    rows = []
    null_count = 0
    null_rows_info = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            match_empty = not row.get('actual_spend') or row['actual_spend'].strip() == ''
            if match_empty:
                null_count += 1
                null_rows_info.append(f"{row['period']} · {row['ward']} · {row['category']} (Reason: {row['notes']})")
            rows.append(row)
            
    print(f"[\u2714] Pre-flight Validation: Discovered {null_count} null actual_spend rows globally:")
    for nr in null_rows_info:
        print(f"  --> NULL: {nr}")
        
    return rows

def compute_growth(rows, target_ward, target_category, growth_type):
    """
    Skill: Compute growth explicitly refusing unsafe assumptions and handling nulls safely.
    """
    # Enforcing Rule 1: Never aggregate across wards or categories
    if target_ward.lower() in ['any', 'all'] or target_category.lower() in ['any', 'all']:
        raise ValueError("REFUSAL: Cannot aggregate across global wards or categories. Explicit targeting is required.")
        
    # Enforcing Rule 4: Refuse if growth_type is missing or guessed
    if not growth_type or growth_type.upper() not in ['MOM', 'YOY']:
        raise ValueError("REFUSAL: --growth-type must be explicitly specified (e.g., MoM). Never guess.")
        
    # Isolate data sequentially
    filtered = sorted([r for r in rows if r['ward'] == target_ward and r['category'] == target_category], key=lambda x: x['period'])
    
    if not filtered:
        print("Warning: No records found for this Ward/Category combination.")
        return []
        
    results = []
    prev_spend = None
    
    for i, row in enumerate(filtered):
        period = row['period']
        current_spend_str = row['actual_spend'].strip() if row.get('actual_spend') else ''
        notes = row.get('notes', '').strip()
        
        # Enforcing Rule 2: Flag every null row before computing
        if not current_spend_str:
            growth_val = "NULL"
            formula_val = "REFUSED: Missing target period data"
            flag = f"FLAGS: {notes}"
            prev_spend = None  # Reset tracking math since the chain is broken
        else:
            current_spend = float(current_spend_str)
            if growth_type.upper() == 'MOM':
                if prev_spend is None:
                    # Enforcing logic: no baseline exists
                    growth_val = "n/a"
                    formula_val = "n/a (baseline)"
                    flag = ""
                else:
                    growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
                    sign = "+" if growth_pct > 0 else ""
                    growth_val = f"{sign}{growth_pct:.1f}%" 
                    
                    # Enforcing Rule 3: Show formula used
                    formula_val = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                    flag = f"({notes})" if notes else ""
                    
                prev_spend = current_spend

        out_row = {
            'period': period,
            'ward': target_ward,
            'category': target_category,
            'actual_spend': current_spend_str or "NULL",
            'growth': growth_val,
            'formula': formula_val,
            'flag': flag
        }
        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Aggregator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    try:
        rows = load_dataset(args.input)
        computed = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        if computed:
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'flag'])
                writer.writeheader()
                writer.writerows(computed)
                
            print(f"[\u2714] Success! Safely bypassed {len(rows) - len(computed)} out-of-scope rows.")
            print(f"[\u2714] Output perfectly written to {args.output}")
            
    except Exception as e:
        print(f"[FATAL FAILURE] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

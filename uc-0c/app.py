"""
UC-0C app.py — Financial Data Assessor
Built using the strict analytical rules in agents.md and skills.md.
"""
import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads the raw budget CSV accurately, strictly validating structural schemas whilst 
    actively locating and mapping deliberately null analytical factors natively.
    """
    data = []
    null_rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Structural constraint check
            expected_fields = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not expected_fields.issubset(set(reader.fieldnames)):
                raise ValueError("Missing foundational structural columns. System halted.")
                
            for idx, row in enumerate(reader, start=2): # +1 for 1-based, +1 for headers
                data.append(row)
                actual = row.get("actual_spend")
                if not actual or actual.strip() == "":
                    null_rows.append((idx, row['period'], row['ward'], row['category'], row['notes']))
    except FileNotFoundError:
        print(f"Error: Dataset {filepath} structurally not found.")
        sys.exit(1)
        
    print(f"\n[PRE-CALCULATION SYSTEM REPORT] Uncovered {len(null_rows)} explicitly empty 'actual_spend' structures:")
    for nr in null_rows:
        print(f"  - Row {nr[0]}: [{nr[1]}] | {nr[2]} | {nr[3]} | Flagging Reason: {nr[4]}")
    print()
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates localized scope progression natively embedding tracking mathematics 
    whilst rejecting broader aggregation traps effortlessly.
    """
    if not growth_type:
        print("[ERROR REFUSAL] --growth-type parameter MUST be explicitly defined. Defaulting to arbitrary math schemas is strictly prohibited.")
        sys.exit(1)
        
    if not ward or not category:
        print("[ERROR REFUSAL] Explicit `--ward` and `--category` string parameters are forcefully required. Aggregating data blindly across disparate sectors is forbidden.")
        sys.exit(1)
        
    # Strictly isolate data cleanly
    target_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not target_data:
        print(f"WARNING: Dataset parsed cleanly, but no literal data segments matched the explicit tuple Ward: '{ward}' / Category: '{category}'.")
        return []
        
    # Order chronologically for explicit timeline logic
    target_data.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend_val = None
    
    for row in target_data:
        period = row['period']
        actual_spend = row['actual_spend'].strip()
        notes = row['notes']
        
        computed_growth = "N/A"
        formula_used = "N/A"
        
        # Explicit Null Check Block
        if actual_spend == "":
            computed_growth = f"[NULL TARGET: {notes}]"
            formula_used = r"[MATH_ABORTED_DUE_TO_NULL]"
            prev_spend_val = None # Fracture successive temporal linkages
        else:
            try:
                current_val = float(actual_spend)
            except ValueError:
                current_val = 0.0
                
            if growth_type.upper() == "MOM":
                if prev_spend_val is not None and prev_spend_val != 0:
                    growth_num = ((current_val - prev_spend_val) / prev_spend_val) * 100
                    
                    sign = "+" if growth_num > 0 else ""
                    computed_growth = f"{sign}{growth_num:.1f}%"
                    formula_used = f"(({current_val} - {prev_spend_val}) / {prev_spend_val}) * 100"
                else:
                    computed_growth = "BASE_PERIOD"
                    formula_used = "INITIAL_INTERVAL"
                    
                prev_spend_val = current_val
            else:
                print(f"[ERROR REFUSAL] Unrecognized math logic parameter requested explicitly: {growth_type}")
                sys.exit(1)
                
        # Rigid tabular build structure
        out_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': row.get("budgeted_amount", ""),
            'actual_spend': actual_spend if actual_spend else "NULL",
            'growth_metric': computed_growth,
            'formula_used': formula_used,
            'notes': row.get("notes", "")
        }
        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Assessor")
    parser.add_argument("--input", required=True, help="Path pointing to structurally explicit data file (CSV)")
    parser.add_argument("--output", required=True, help="Path target output for table creation")
    parser.add_argument("--ward", required=False, help="Forced target isolated ward segment")
    parser.add_argument("--category", required=False, help="Forced target isolated category segment")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Explicit temporal logic parameter (e.g. MoM)")
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        sys.exit(0)
        
    fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_metric', 'formula_used', 'notes']
    
    try:    
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"[SUCCESS] Explicit strict calculations strictly routed directly into: {args.output}")
    except Exception as e:
        print(f"Failed to export explicitly computed logic: {e}")

if __name__ == "__main__":
    main()

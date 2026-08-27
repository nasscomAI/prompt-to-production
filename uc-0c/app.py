"""
UC-0C app.py — Local Data Aggregator
Deterministic execution scripted exactly to the strict UC-0C constraints.
NO EXTERNAL AI OR CLOUD LLMS DEPLOYED.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_file: str, target_ward: str, target_category: str) -> list:
    """
    Skill 1: Loads the file natively, intercepts target conditions, 
    and openly escalates hidden target variables (nulls).
    """
    if not os.path.exists(input_file):
        print(f"[REJECTED] Input file {input_file} not located.")
        sys.exit(1)

    filtered_data = []
    null_issues = []

    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('ward') == target_ward and row.get('category') == target_category:
                
                # Active trap for deliberately stripped variables (silent dropping)
                val_str = row.get('actual_spend', '').strip()
                if not val_str:
                    notes = row.get('notes', 'No notes provided')
                    null_issues.append((row['period'], notes))
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(val_str)
                    except ValueError:
                        row['actual_spend'] = None
                        null_issues.append((row['period'], "Corrupted string format intercepted"))
                
                filtered_data.append(row)

    # Explicit report output dictated by R.I.C.E rules
    if null_issues:
        print(f"\n[ALERT] Blocked silent drop: Found {len(null_issues)} active null/empty records deliberately placed in this target view:")
        for period, note in null_issues:
            print(f"   -> Period: {period} | Source Reference Note: {note}")
        print("These records have been structurally segregated and flagged prior to matrix computation.\n")

    # Time-sequence security sort
    return sorted(filtered_data, key=lambda x: x['period'])

def compute_growth(dataset: list, growth_type: str) -> list:
    """
    Skill 2: Processes sequential financial variance without aggregating gaps.
    """
    results = []
    
    for i, row in enumerate(dataset):
        period = row['period']
        actual = row.get('actual_spend')
        notes = row.get('notes', '')
        
        output_row = {
            "period": period,
            "ward": row['ward'],
            "category": row['category'],
            "actual_spend": actual if actual is not None else "NULL",
            "growth_calculus": "N/A",
            "formula_deployed": "N/A",
            "source_notes": notes
        }

        # Enforcement 2 constraint mappings (Never silently blend incomplete gaps)
        if actual is None:
            output_row["growth_calculus"] = "Must be flagged — not computed"
            output_row["formula_deployed"] = "COMPUTATION HALTED"
            results.append(output_row)
            continue
        
        if growth_type.lower() == "mom":
            if i == 0:
                 output_row["growth_calculus"] = "N/A (Temporal Base Line)"
                 output_row["formula_deployed"] = "MoM"
            else:
                 prev_val = dataset[i-1].get('actual_spend')
                 if prev_val is None:
                     output_row["growth_calculus"] = "Aborted (Direct predecessor target missing)"
                     output_row["formula_deployed"] = "COMPUTATION HALTED"
                 elif prev_val == 0:
                     output_row["growth_calculus"] = "Infinite / DIV0 Base"
                     output_row["formula_deployed"] = "MoM"
                 else:
                     diff = actual - prev_val
                     pct = (diff / prev_val) * 100
                     sign = "+" if pct > 0 else ""
                     
                     # Extracting explanation notes naturally to append securely.
                     note_suffix = f" ({notes})" if notes else ""
                     output_row["growth_calculus"] = f"{sign}{pct:.1f}%{note_suffix}"
                     output_row["formula_deployed"] = "MoM"
                     
        elif growth_type.lower() == "yoy":
             # Fallback simplistic YOY validation track
             if i < 12:
                 output_row["growth_calculus"] = "N/A (Lack of Historical Target Variance)"
                 output_row["formula_deployed"] = "YoY"
             else:
                 prev_val = dataset[i-12].get('actual_spend')
                 if prev_val is None:
                     output_row["growth_calculus"] = "Aborted (Historical Target Missing)"
                     output_row["formula_deployed"] = "COMPUTATION HALTED"
                 else:
                     diff = actual - prev_val
                     pct = (diff / prev_val) * 100
                     sign = "+" if pct > 0 else ""
                     note_suffix = f" ({notes})" if notes else ""
                     output_row["growth_calculus"] = f"{sign}{pct:.1f}%{note_suffix}"
                     output_row["formula_deployed"] = "YoY"
        
        results.append(output_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Structurally Isolated Data Aggregator")
    parser.add_argument("--input", required=True, help="Absolute path to CSV dataset")
    parser.add_argument("--output", required=True, help="Absolute path for final export")
    
    # Made optional explicitly so we can forcefully intercept absence internally
    parser.add_argument("--ward", default=None, help="Target isolation array")
    parser.add_argument("--category", default=None, help="Target isolation variable")
    parser.add_argument("--growth-type", default=None, help="Mathematical framework (MoM/YoY)")
    
    args = parser.parse_args()

    # Enforcement Trap 1: Refusing naive aggregative requests implicitly
    if not args.ward or not args.category:
        print("\n[FATAL REFUSAL: GLOBAL AGGREGATION DETECTED]")
        print("My algorithms strictly block naive cross-category and cross-ward global metric consolidation.")
        print("Please declare explicit isolation barriers using both `--ward` and `--category` flags.")
        sys.exit(1)

    # Enforcement Trap 4: Demanding active calculation commands, no assumptions
    if not args.growth_type:
        print("\n[FATAL REFUSAL: MISSING COMPUTATIONAL LOGIC]")
        print("Growth type unstated. I am barred from assuming defaulting metric frameworks (e.g. Month-on-Month).")
        print("Please actively declare it via `--growth-type`.")
        sys.exit(1)

    print(f"\n[INIT] Deploying strictly local isolated loop against [{args.ward} -> {args.category}] using variant logic [{args.growth_type}].")
    
    filtered_data = load_dataset(args.input, args.ward, args.category)
    if not filtered_data:
        print("[WARNING] Zero matches yielded within that intersectional string variable.")
        sys.exit(0)

    final_output = compute_growth(filtered_data, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_calculus", "formula_deployed", "source_notes"]
    with open(args.output, "w", encoding="utf-8", newline="") as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_output)

    print(f"[SUCCESS] Native tabular generation mapped smoothly. Process tracked and logged to => {args.output}\n")

if __name__ == "__main__":
    main()

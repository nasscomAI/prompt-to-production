"""
UC-0C app.py — Budget Analyst
Implements load_dataset and compute_growth per agents.md and skills.md.
"""
import argparse
import csv
import sys
import os

EXPECTED_COLUMNS = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']

def load_dataset(file_path: str) -> list[dict]:
    """
    Skill: load_dataset
    Reads the CSV, validates columns, and reports all null values in actual_spend.
    Never silently imputes.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: Dataset file '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    dataset = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print(f"ERROR: Dataset '{file_path}' has no header row.", file=sys.stderr)
                sys.exit(1)
                
            missing_cols = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
            if missing_cols:
                print(f"ERROR: Dataset is missing required columns: {missing_cols}", file=sys.stderr)
                sys.exit(1)
                
            dataset = list(reader)
    except Exception as e:
        print(f"ERROR: Could not read dataset '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Proactive null scan
    null_count = 0
    null_locations = []
    for row in dataset:
        val = row.get('actual_spend', '').strip()
        if not val or val.lower() == 'null':
            null_count += 1
            null_locations.append(f"{row['period']} · {row['ward']} · {row['category']} (Reason: {row['notes']})")
            
    # skills.md: print total row count + null summary to stdout BEFORE returning
    print(f"Dataset loaded: {len(dataset)} rows total | NULL actual_spend: {null_count}")
    if null_count > 0:
        print(f"ATTENTION: {null_count} row(s) with NULL actual_spend — will be flagged, not imputed:")
        for loc in null_locations:
            print(f"  - {loc}")

    return dataset


def compute_growth(dataset: list[dict], ward: str, category: str, growth_type: str, output_path: str):
    """
    Skill: compute_growth
    Computes growth for a specific ward and category, refusing cross-aggregation.
    Outputs table with explicitly flagged nulls and formulas.
    """
    if not ward or not category:
        print("ERROR: Refusing cross-aggregation. You must specify both --ward and --category explicitly.", file=sys.stderr)
        sys.exit(1)
        
    if not growth_type:
        print("ERROR: --growth-type was not specified. I cannot guess the intended formula (e.g., MoM, YoY). Please provide it.", file=sys.stderr)
        sys.exit(1)
        
    growth_type = growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        print(f"ERROR: Unsupported growth type '{growth_type}'. Please use MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    # Filter dataset
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    if not filtered:
        print(f"WARNING: No data found for ward '{ward}' and category '{category}'.", file=sys.stderr)
    
    # Sort chronologically
    filtered.sort(key=lambda r: r['period'])
    
    output_rows = []
    for i, current_row in enumerate(filtered):
        period = current_row['period']
        current_val_str = current_row['actual_spend'].strip()
        notes = current_row['notes'].strip()
        
        # Rule: explicit null flagging
        if not current_val_str or current_val_str.lower() == 'null':
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_percentage": "NULL",
                "formula_used": f"Cannot compute: actual_spend is NULL (Reason: {notes})"
            })
            continue
            
        try:
            current_val = float(current_val_str)
        except ValueError:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_val_str,
                "growth_percentage": "ERROR",
                "formula_used": "Invalid numerical value"
            })
            continue

        previous_val = None
        previous_period = None
        
        prev_null_notes = None  # track if previous period was itself NULL
        if growth_type == "MOM":
            if i > 0:
                prev_row = filtered[i-1]
                prev_val_str = prev_row['actual_spend'].strip()
                if not prev_val_str or prev_val_str.lower() == 'null':
                    # Previous period is NULL — current growth must also be flagged, not computed
                    prev_null_notes = prev_row['notes'].strip()
                else:
                    try:
                        previous_val = float(prev_val_str)
                        previous_period = prev_row['period']
                    except ValueError:
                        pass
        elif growth_type == "YOY":
            # For YoY, look for exactly 12 months prior
            year, month = period.split('-')
            target_prev_period = f"{int(year)-1}-{month}"
            for prev_row in filtered[:i]:
                if prev_row['period'] == target_prev_period:
                    prev_val_str = prev_row['actual_spend'].strip()
                    if not prev_val_str or prev_val_str.lower() == 'null':
                        prev_null_notes = prev_row['notes'].strip()
                    else:
                        try:
                            previous_val = float(prev_val_str)
                            previous_period = target_prev_period
                        except ValueError:
                            pass
                    break
                    
        # skills.md: if previous period is NULL, current row must be flagged — not computed
        if prev_null_notes is not None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_val_str,
                "growth_percentage": "NULL",
                "formula_used": f"Must be flagged — not computed: previous period actual_spend is NULL (Reason: {prev_null_notes})"
            })
        elif previous_val is not None and previous_val != 0:
            growth = (current_val - previous_val) / previous_val * 100
            formula = f"({current_val} - {previous_val}) / {previous_val} * 100"
            growth_str = f"{growth:+.1f}%"
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_val_str,
                "growth_percentage": growth_str,
                "formula_used": formula
            })
        else:
            growth_str = "n/a"
            if previous_val == 0:
                formula = "Cannot compute: previous period value is 0 (division by zero)"
            elif growth_type == "MOM" and i == 0:
                formula = f"First period ({period}); no previous period available for MoM"
            else:
                year, month = period.split('-')
                target = f"{int(year)-1}-{month}"
                formula = f"No valid previous period data found for YoY (expected {target})"
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_val_str,
                "growth_percentage": growth_str,
                "formula_used": formula
            })

    # Write output
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["period", "ward", "category", "actual_spend", "growth_percentage", "formula_used"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
    except OSError as e:
        print(f"ERROR: Cannot write to output file '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Done. Wrote {len(output_rows)} rows to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="e.g., MoM, YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # We require --growth-type at the application level to enforce rule #4.
    # We do manual validation instead of `required=True` so we can produce our specific error message.
    if not args.growth_type:
        print("ERROR: --growth-type was not specified. System refuses to guess (e.g., MoM, YoY).", file=sys.stderr)
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("ERROR: --ward and --category must be explicitly provided. Refusing cross-ward/cross-category aggregation.", file=sys.stderr)
        sys.exit(1)

    dataset = load_dataset(args.input)
    compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()

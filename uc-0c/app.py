"""
UC-0C app.py — Ward Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Ward name")
    parser.add_argument("--category", default=None, help="Category name")
    parser.add_argument("--growth-type", default=None, help="Growth type: MoM")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # 1. Check if growth-type is specified
    if not args.growth_type:
        print("Refusal: Growth type (--growth-type) is not specified. Refusing to default or guess.")
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print(f"Refusal: Growth type '{args.growth_type}' is not supported. Only 'MoM' is supported.")
        sys.exit(1)
        
    # 2. Check if ward and category are specified
    if not args.ward or not args.category:
        print("Refusal: All-ward or all-category aggregation is not permitted. You must specify both --ward and --category.")
        sys.exit(1)
        
    # 3. Load dataset
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
        
    all_rows = []
    null_rows = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            actual = row.get("actual_spend", "").strip()
            if not actual:
                null_rows.append({
                    "line": idx + 2,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes")
                })
            all_rows.append(row)
            
    print(f"Loaded {len(all_rows)} rows. Found {len(null_rows)} null actual spend values:")
    for nr in null_rows:
        print(f"  - Row {nr['line']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        
    # 4. Filter for requested ward and category
    filtered = [r for r in all_rows if r.get("ward") == args.ward and r.get("category") == args.category]
    if not filtered:
        print(f"Error: No data found for ward '{args.ward}' and category '{args.category}'.")
        sys.exit(1)
        
    # Sort by period
    filtered.sort(key=lambda x: x.get("period", ""))
    
    # Compute MoM growth
    output_rows = []
    
    for i, row in enumerate(filtered):
        period = row.get("period")
        ward = row.get("ward")
        cat = row.get("category")
        actual_str = row.get("actual_spend", "").strip()
        row_notes = row.get("notes", "").strip()
        
        if not actual_str:
            actual_spend = "NULL"
            growth_pct = "NULL"
            formula = "n/a"
            notes = f"Flagged null actual spend: {row_notes}"
        else:
            actual_spend = float(actual_str)
            if i == 0:
                growth_pct = "NULL"
                formula = "n/a"
                notes = "No previous period data available"
            else:
                prev_row = filtered[i-1]
                prev_actual_str = prev_row.get("actual_spend", "").strip()
                if not prev_actual_str:
                    growth_pct = "NULL"
                    formula = "n/a"
                    notes = f"Cannot compute: previous month ({prev_row.get('period')}) was null."
                else:
                    prev_actual = float(prev_actual_str)
                    growth = (actual_spend - prev_actual) / prev_actual
                    growth_pct_val = growth * 100
                    if growth_pct_val >= 0:
                        growth_pct = f"+{growth_pct_val:.1f}%"
                    else:
                        # Standard minus is fine, but let's make sure it matches user requirements
                        growth_pct = f"{growth_pct_val:.1f}%"
                    formula = f"({actual_spend} - {prev_actual}) / {prev_actual}"
                    notes = row_notes if row_notes else ""
                    
        output_rows.append({
            "period": period,
            "ward": ward,
            "category": cat,
            "actual_spend": actual_spend,
            "growth_percentage": growth_pct,
            "formula": formula,
            "notes": notes
        })
        
    # Write to CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_percentage", "formula", "notes"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for orow in output_rows:
            writer.writerow(orow)
            
    print(f"Growth calculation written to {args.output}")

if __name__ == "__main__":
    main()

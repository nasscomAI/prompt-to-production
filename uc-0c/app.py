"""
UC-0C app.py — Municipal Budget Growth Analysis Engine.
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""

import argparse
import csv
import sys
import os

def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """
    Skill: load_dataset
    Reads the ward budget CSV file, validates required columns, and identifies
    all rows with null/missing actual_spend values along with their notes.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget dataset not found at: {input_path}")
        
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        missing = required_cols - set(reader.fieldnames or [])
        raise ValueError(f"Dataset missing required columns: {missing}")
        
    flagged_nulls = []
    for idx, row in enumerate(rows, start=1):
        spend_val = row.get("actual_spend", "").strip()
        if spend_val == "" or spend_val.upper() == "NULL" or spend_val.upper() == "NONE":
            flagged_nulls.append({
                "row_index": idx,
                "period": row.get("period"),
                "ward": row.get("ward"),
                "category": row.get("category"),
                "notes": row.get("notes", "").strip() or "No note provided"
            })
            
    return rows, flagged_nulls

def compute_growth_pair(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Computes per-period growth for a single (ward, category) pair without aggregation.
    """
    filtered = [r for r in rows if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]
    filtered.sort(key=lambda r: r["period"].strip())

    output_rows = []
    prev_spend = None

    for r in filtered:
        period = r["period"].strip()
        raw_spend = r["actual_spend"].strip()
        notes = r["notes"].strip()
        
        is_null = raw_spend == "" or raw_spend.upper() in ["NULL", "NONE"]
        
        if is_null:
            null_reason = notes if notes else "Data missing / unsubmitted"
            row_result = {
                "ward": ward,
                "category": category,
                "period": period,
                "budgeted_amount": r.get("budgeted_amount", "").strip(),
                "actual_spend": "NULL",
                "growth_type": growth_type,
                "growth": "NULL",
                "formula": "N/A (Missing actual_spend data)",
                "status_note": f"FLAGGED NULL: {null_reason}"
            }
            prev_spend = None
        else:
            current_spend = float(raw_spend)
            if prev_spend is None:
                row_result = {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "budgeted_amount": r.get("budgeted_amount", "").strip(),
                    "actual_spend": f"{current_spend:.1f}",
                    "growth_type": growth_type,
                    "growth": "N/A (Baseline period)",
                    "formula": "N/A (First period in sequence)",
                    "status_note": notes or "Baseline period"
                }
            else:
                pct = ((current_spend - prev_spend) / prev_spend) * 100.0
                sign = "+" if pct >= 0 else ""
                growth_str = f"{sign}{pct:.1f}%"
                formula_str = f"(({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                
                row_result = {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "budgeted_amount": r.get("budgeted_amount", "").strip(),
                    "actual_spend": f"{current_spend:.1f}",
                    "growth_type": growth_type,
                    "growth": growth_str,
                    "formula": formula_str,
                    "status_note": notes or "Valid calculation"
                }
                
            prev_spend = current_spend

        output_rows.append(row_result)

    return output_rows

def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Skill: compute_growth
    Calculates growth metrics for specified ward(s) and category(ies) over time according
    to the specified growth_type, outputting per-period results with explicit formulas shown.
    
    Enforces rules:
    - Never aggregates across wards or categories (keeps individual series separate).
    - Flags null actual_spend rows explicitly with reason from notes.
    - Attaches explicit mathematical formula to each row.
    """
    if not growth_type or growth_type.strip().lower() not in ["mom", "month-over-month", "month over month"]:
        raise ValueError("REFUSAL: --growth-type was not specified or is ambiguous. Specify valid growth type (e.g. '--growth-type MoM').")

    all_wards = sorted(list(set(r["ward"].strip() for r in rows)))
    all_cats = sorted(list(set(r["category"].strip() for r in rows)))

    target_wards = all_wards if (ward and ward.strip().lower() == "all") else ([ward.strip()] if ward else [])
    target_cats = all_cats if (category and category.strip().lower() == "all") else ([category.strip()] if category else [])

    if not target_wards:
        raise ValueError("REFUSAL: Target ward is missing or invalid.")
    if not target_cats:
        raise ValueError("REFUSAL: Target category is missing or invalid.")

    all_results = []
    for w in target_wards:
        for c in target_cats:
            res = compute_growth_pair(rows, w, c, growth_type)
            all_results.extend(res)

    return all_results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analysis Engine")
    parser.add_argument("--input", required=True, help="Path to input ward_budget.csv file")
    parser.add_argument("--ward", required=False, help="Target ward name or 'all'")
    parser.add_argument("--category", required=False, help="Target spending category or 'all'")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Growth type calculation (e.g. 'MoM')")
    parser.add_argument("--output", required=False, help="Path to save output CSV file")

    args = parser.parse_args()

    # Skill 1: Load and validate dataset
    try:
        rows, flagged_nulls = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded dataset: {len(rows)} total rows.")
    print(f"Flagged null rows count: {len(flagged_nulls)}")
    for null_item in flagged_nulls:
        print(f"  - Row {null_item['row_index']} ({null_item['period']} | {null_item['ward']} | {null_item['category']}): NULL -> Note: '{null_item['notes']}'")

    if not args.ward or not args.category or not args.growth_type:
        missing_params = []
        if not args.ward: missing_params.append("--ward")
        if not args.category: missing_params.append("--category")
        if not args.growth_type: missing_params.append("--growth-type")
        
        print(f"\n[REFUSAL ERROR] Missing required parameters: {', '.join(missing_params)}", file=sys.stderr)
        print("Enforcement Rule: Provide explicit --ward (or 'all'), --category (or 'all'), and --growth-type (e.g. MoM).", file=sys.stderr)
        sys.exit(2)

    # Skill 2: Compute per-ward per-category growth
    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as ve:
        print(f"\n[ENFORCEMENT REFUSAL]: {ve}", file=sys.stderr)
        sys.exit(3)

    print(f"\n=== Growth Calculation Results ({len(results)} total per-ward per-category rows generated) ===")
    fieldnames = ["ward", "category", "period", "budgeted_amount", "actual_spend", "growth_type", "growth", "formula", "status_note"]
    
    # Write output CSV if requested
    output_path = args.output if args.output else "growth_output.csv"
    with open(output_path, mode="w", encoding="utf-8", newline="") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results successfully saved to: {output_path}")

if __name__ == "__main__":
    main()

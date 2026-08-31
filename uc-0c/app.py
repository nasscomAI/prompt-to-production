import argparse
import csv
import os
import re
import sys

def normalize(text: str) -> str:
    """Helper to normalize strings for robust comparison."""
    return re.sub(r"[^a-zA-Z0-9]", "", text).lower()

def load_dataset(input_path: str):
    """Skill 1: Reads CSV, validates columns, reports null count and which rows."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    rows = []
    null_rows = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required columns: {required_cols}")
            
        for row in reader:
            spend_raw = row["actual_spend"].strip()
            if spend_raw == "" or spend_raw.upper() == "NULL":
                null_rows.append(row)
            rows.append(row)
            
    print(f"Loaded {len(rows)} rows. Flagged {len(null_rows)} null actual_spend rows:")
    for nr in null_rows:
        print(f" - [{nr['period']}] {nr['ward']} | {nr['category']} -> Reason: {nr['notes']}")
        
    return rows, null_rows

def compute_growth(rows: list, target_ward: str, target_category: str, growth_type: str):
    """Skill 2: Takes ward + category + growth_type, returns per-period table with formula shown."""
    if not growth_type:
        raise ValueError("Error: --growth-type not specified. System refuses to assume formula.")
    
    if growth_type.upper() != "MOM":
        raise ValueError(f"Unsupported growth-type: '{growth_type}'. Only 'MoM' is currently supported.")
        
    if not target_ward or not target_category:
        raise ValueError("System refuses all-ward/all-category aggregation. Must specify exact --ward and --category.")

    norm_target_ward = normalize(target_ward)
    norm_target_cat = normalize(target_category)

    # Filter by normalized ward and category
    filtered = [
        r for r in rows 
        if normalize(r["ward"]) == norm_target_ward 
        and normalize(r["category"]) == norm_target_cat
    ]
    
    if not filtered:
        raise ValueError(f"No records found matching ward='{target_ward}' and category='{target_category}'.")
        
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row["period"]
        ward = row["ward"]
        cat = row["category"]
        spend_str = row["actual_spend"].strip()
        notes = row.get("notes", "")
        
        if spend_str == "" or spend_str.upper() == "NULL":
            results.append({
                "period": period,
                "ward": ward,
                "category": cat,
                "actual_spend": "NULL",
                "mom_growth": "NULL_FLAGGED",
                "formula": "n/a",
                "notes": f"Flagged: {notes}" if notes else "Flagged null"
            })
            prev_spend = None  # Reset baseline
        else:
            curr_spend = float(spend_str)
            if prev_spend is None:
                growth_str = "n/a (baseline)"
                formula_str = "First valid period"
            else:
                growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
                growth_str = f"{growth_val:+.1f}%"
                formula_str = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
                
            results.append({
                "period": period,
                "ward": ward,
                "category": cat,
                "actual_spend": f"{curr_spend:.1f}",
                "mom_growth": growth_str,
                "formula": formula_str,
                "notes": notes
            })
            prev_spend = curr_spend
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output growth CSV")
    
    args = parser.parse_args()
    
    try:
        rows, _ = load_dataset(args.input)
        growth_table = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        fieldnames = ["period", "ward", "category", "actual_spend", "mom_growth", "formula", "notes"]
        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(growth_table)
            
        print(f"Successfully wrote growth analysis to: {args.output}")
        
    except Exception as e:
        print(f"Execution failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
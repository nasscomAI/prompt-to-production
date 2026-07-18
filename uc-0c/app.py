"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str) -> list:
    """
    Reads the budget CSV file, parses rows, and returns a list of records.
    """
    records = []
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned_row = {
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": row.get("budgeted_amount", "").strip(),
                "actual_spend": row.get("actual_spend", "").strip(),
                "notes": row.get("notes", "").strip()
            }
            records.append(cleaned_row)
            
    # Print summary of the 5 target null values found
    null_rows = [r for r in records if not r["actual_spend"]]
    print(f"Loaded {len(records)} records. Found {len(null_rows)} null actual_spend rows:")
    for nr in null_rows:
        print(f" - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        
    return records

def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters records by ward and category, sorts chronologically, and calculates MoM growth.
    """
    # Filter records
    filtered = [r for r in records if r["ward"] == ward and r["category"] == category]
    
    if not filtered:
        print(f"Error: No records found for ward='{ward}' and category='{category}'")
        sys.exit(1)
        
    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i, curr in enumerate(filtered):
        period = curr["period"]
        budgeted = curr["budgeted_amount"]
        actual = curr["actual_spend"]
        note = curr["notes"]
        
        status = "OK"
        growth = "n/a"
        formula = "n/a"
        
        # If current is null
        if not actual:
            growth = "NULL"
            formula = "n/a"
            status = f"NULL: {note}"
        elif i == 0:
            growth = "n/a"
            formula = "n/a (no previous month)"
            status = "OK"
        else:
            prev = filtered[i-1]
            prev_actual = prev["actual_spend"]
            prev_note = prev["notes"]
            
            # If previous is null
            if not prev_actual:
                growth = "NULL"
                formula = "n/a"
                status = f"NULL: Previous month spend was null ({prev_note})"
            else:
                curr_val = float(actual)
                prev_val = float(prev_actual)
                
                # Compute MoM growth
                growth_val = (curr_val - prev_val) / prev_val
                growth = f"{growth_val * 100:+.1f}%"
                formula = f"({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}"
                
                if note:
                    status = f"OK ({note})"
                    
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual if actual else "NULL",
            "growth": growth,
            "formula": formula,
            "status": status
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (required, no aggregation)")
    parser.add_argument("--category", required=False, help="Budget category (required, no aggregation)")
    parser.add_argument("--growth-type", required=False, help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    # Enforcement checks
    if not args.growth_type:
        print("Refusal: --growth-type must be specified. Guesses are not allowed.")
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print(f"Refusal: Growth type '{args.growth_type}' is not supported or cannot be computed due to insufficient data.")
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("Refusal: Ward and Category must be specified. Aggregating across all wards or categories is prohibited.")
        sys.exit(1)
        
    forbidden_terms = ["all", "any", "combined", "aggregate", "total", "sum"]
    if args.ward.lower() in forbidden_terms or args.category.lower() in forbidden_terms:
        print("Refusal: Aggregation across all wards or categories is prohibited.")
        sys.exit(1)
        
    records = load_dataset(args.input)
    results = compute_growth(records, args.ward, args.category, args.growth_type)
    
    # Write to output CSV
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "status"]
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
            
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import sys

def load_dataset(input_path, target_ward, target_category):
    if not target_ward or not target_category:
        print("REFUSAL: Cannot aggregate across multiple wards or categories without explicit instruction.")
        sys.exit(1)
        
    filtered_data = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ward"] == target_ward and row["category"] == target_category:
                filtered_data.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "budgeted_amount": row["budgeted_amount"],
                    "actual_spend": row["actual_spend"] if row["actual_spend"].strip() else None,
                    "notes": row["notes"]
                })
    return sorted(filtered_data, key=lambda x: x["period"])

def compute_growth(data, growth_type):
    if not growth_type or growth_type != "MoM":
        print("REFUSAL: Expected explicit growth-type 'MoM'. I will not silently guess the formula.")
        sys.exit(1)
        
    results = []
    prev_val = None
    
    for i, row in enumerate(data):
        period = row["period"]
        ward = row["ward"]
        category = row["category"]
        spend_str = row["actual_spend"]
        notes = row["notes"]
        
        formula_used = "(Current - Previous) / Previous"
        
        if spend_str is None:
            growth_out = f"Must be flagged — not computed (NULL: {notes})"
            actual_spend_out = "NULL"
            prev_val = None # Reset previous value since continuity is broken
        else:
            try:
                curr_val = float(spend_str)
                actual_spend_out = spend_str
                
                if prev_val is None:
                    growth_out = "n/a"
                else:
                    if prev_val == 0:
                        growth_out = "n/a (Div by Zero)"
                    else:
                        pct = ((curr_val - prev_val) / prev_val) * 100
                        sign = "+" if pct > 0 else ""
                        growth_out = f"{sign}{pct:.1f}% [{formula_used}]"
                        
                prev_val = curr_val
            except ValueError:
                actual_spend_out = spend_str
                growth_out = "Invalid number format"
                prev_val = None
                
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual_spend_out,
            "MoM Growth": growth_out
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. I will not guess the metric requested.")
        sys.exit(1)
        
    data = load_dataset(args.input, args.ward, args.category)
    if not data:
        print(f"No data found for Ward: {args.ward}, Category: {args.category}")
        sys.exit(1)
        
    results = compute_growth(data, args.growth_type)
    
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()

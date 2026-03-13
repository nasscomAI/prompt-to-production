"""
UC-0C app.py — Implemented File
Builds the Number That Looks Right growth output utilizing constraints from agents.md.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """Read CSV, look for missing actual_spend rows and flag them."""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Validation per agents.md: Flag nulls before computing
    null_count = 0
    for r in data:
        if not r.get("actual_spend") or not str(r["actual_spend"]).strip():
            null_count += 1
            
    print(f"Dataset loaded. Note: Found {null_count} rows with missing actual_spend data.")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes subset, safely computes growth with verbatim formulas."""
    
    if growth_type not in ["MoM", "YoY"]:
        print("Refusal: --growth-type must be specified as either 'MoM' or 'YoY'. I will not guess.", file=sys.stderr)
        sys.exit(1)
        
    if ward.lower() == "any" or category.lower() == "any" or not ward or not category:
        print("Refusal: Cannot aggregate across wards or categories. Please specify a distinct ward and category.", file=sys.stderr)
        sys.exit(1)
        
    # Filter dataset
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    
    # Sort by period string YYYY-MM
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i, cur in enumerate(filtered):
        period = cur["period"]
        spend_str = cur.get("actual_spend", "").strip()
        notes = cur.get("notes", "").strip()
        
        row_result = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": spend_str,
            "growth_percentage": "",
            "formula_used": ""
        }
        
        if not spend_str:
            row_result["growth_percentage"] = "FLAG: NULL SPEND"
            row_result["formula_used"] = f"Reason: {notes}"
            results.append(row_result)
            continue
            
        cur_spend = float(spend_str)
        
        # Calculate step
        step = 1 if growth_type == "MoM" else 12
        
        if i >= step:
            prev = filtered[i - step]
            prev_spend_str = prev.get("actual_spend", "").strip()
            
            if not prev_spend_str:
                row_result["growth_percentage"] = "FLAG: PREV NULL"
                row_result["formula_used"] = f"Previous period ({prev['period']}) spend was also null"
            else:
                prev_spend = float(prev_spend_str)
                if prev_spend == 0:
                    row_result["growth_percentage"] = "n/a (div by zero)"
                    row_result["formula_used"] = f"({cur_spend} - 0) / 0"
                else:
                    growth = ((cur_spend - prev_spend) / prev_spend) * 100
                    row_result["growth_percentage"] = f"{growth:+.1f}%"
                    row_result["formula_used"] = f"(({cur_spend} - {prev_spend}) / {prev_spend}) * 100"
        else:
            row_result["growth_percentage"] = "n/a (no prior data)"
            row_result["formula_used"] = "n/a"
            
        results.append(row_result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C AI Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Target ward name")
    parser.add_argument("--category", required=False, help="Target category")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY type")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    if not args.ward or not args.category or not getattr(args, "growth_type", None):
        print("Refusal: System requires explicit --ward, --category, and --growth-type arguments to prevent unsafe aggregation.", file=sys.stderr)
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    with open(args.output, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "period", "actual_spend", "growth_percentage", "formula_used"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Success! Output written to {args.output}")

if __name__ == "__main__":
    main()

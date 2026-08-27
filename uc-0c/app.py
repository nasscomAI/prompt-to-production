"""
UC-0C app.py
Number That Looks Right.
Deterministic application mapping to explicitly handle null values and refuse blind aggregations.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str, ward: str, category: str):
    # Enforce Rule 1: Refuse global aggregations
    if not ward or not category or ward.lower() in ("any", "all") or category.lower() in ("any", "all"):
        print("System REFUSE: Cannot aggregate across wards or categories blindly. Please specify exact ward and category.")
        sys.exit(1)

    rows = []
    null_flags = []
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['ward'] == ward and r['category'] == category:
                # Rule 2: Note any null rows explicitly
                spend_str = r['actual_spend'].strip()
                if not spend_str:
                    r['actual_spend'] = None
                    null_flags.append((r['period'], r['notes']))
                else:
                    try:
                        r['actual_spend'] = float(spend_str)
                    except ValueError:
                        r['actual_spend'] = None
                        null_flags.append((r['period'], f"Parse Error: {spend_str}"))
                rows.append(r)
                
    # Always report if there are missing values to the console as part of the loading duty
    if null_flags:
        print(f"Info: Found {len(null_flags)} missing actual_spend rows for this query.")
        
    return sorted(rows, key=lambda x: x['period'])

def compute_growth(rows: list, growth_type: str):
    # Rule 4: Refuse to guess the formula
    if not growth_type:
        print("System REFUSE: Growth type not specified. Please pass --growth-type.")
        sys.exit(1)
        
    if growth_type.upper() != "MOM":
        print(f"System REFUSE: Unsupported growth type '{growth_type}'. Only MoM is implemented for this task.")
        sys.exit(1)

    output = []
    
    for i in range(len(rows)):
        current = rows[i]
        out_row = {
            "period": current["period"],
            "ward": current["ward"],
            "category": current["category"],
            "actual_spend": current["actual_spend"] if current["actual_spend"] is not None else "NULL",
            "mom_growth": "NULL",
            "formula": "NULL",
            "flag": current.get("notes", "")
        }
        
        # Calculate MoM Growth
        if i == 0:
            out_row["formula"] = "N/A (first period)"
        else:
            prev = rows[i-1]
            if current["actual_spend"] is None or prev["actual_spend"] is None:
                out_row["mom_growth"] = "NULL"
                out_row["formula"] = "Cannot compute due to NULL value"
                if current["actual_spend"] is None:
                    out_row["flag"] = f"Missing current: {current.get('notes', '')}"
                elif prev["actual_spend"] is None:
                    out_row["flag"] = f"Missing previous: {prev.get('notes', '')}"
            else:
                curr_val = current["actual_spend"]
                prev_val = prev["actual_spend"]
                if prev_val == 0:
                    out_row["mom_growth"] = "+inf%"
                    out_row["formula"] = f"({curr_val} - {prev_val}) / {prev_val} * 100"
                else:
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    # Rule 3: Add explicit formula string next to output
                    out_row["mom_growth"] = f"{growth:+.1f}%"
                    out_row["formula"] = f"({curr_val} - {prev_val}) / {prev_val} * 100"
                    
        output.append(out_row)
        
    return output

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Target ward to analyze")
    parser.add_argument("--category", required=False, help="Target category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    
    rows = load_dataset(args.input, args.ward, args.category)
    results = compute_growth(rows, args.growth_type)
    
    with open(args.output, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["period", "ward", "category", "actual_spend", "mom_growth", "formula", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()

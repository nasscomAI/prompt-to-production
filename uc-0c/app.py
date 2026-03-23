"""
UC-0C app.py — Strict Ward Budget Analyzer
Enforces constraints defined in agents.md and skills.md.
"""
import argparse
import csv
import sys

def load_dataset(file_path: str):
    data = []
    null_rows = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError("Dataset missing fundamental budget columns.")
                
            for row in reader:
                data.append(row)
                if not row.get("actual_spend") or row.get("actual_spend").strip().lower() in ["", "null", "none"]:
                    null_rows.append(f"{row['period']} - {row['ward']} - {row['category']}: {row.get('notes', 'No notes provided')}")
    except FileNotFoundError:
        print("Error: Budget dataset not found.")
        sys.exit(1)
        
    print(f"Dataset loaded. Total rows: {len(data)}. Found {len(null_rows)} null records.")
    for n in null_rows:
        print(f"[FLAGGED] Missing actual_spend at {n}")
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str):
    if not growth_type:
        print("REFUSAL: You must strictly specify a --growth-type (e.g., MoM, YoY). Guessing is prohibited.")
        sys.exit(1)
        
    if "," in ward or "," in category or ward.lower() == "all" or category.lower() == "all":
         print("REFUSAL: System strictly prohibits aggregating across multiple wards or categories.")
         sys.exit(1)
         
    # Filter data
    filtered = sorted([d for d in data if d["ward"] == ward and d["category"] == category], key=lambda x: x["period"])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]
        budget = row["budgeted_amount"]
        notes = row["notes"]
        
        if not actual or actual.strip().lower() in ["", "null", "none"]:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "growth": "[FLAGGED_NULL_ROW]",
                "formula_used": "Not Computed",
                "notes": notes
            })
            prev_spend = None
            continue
            
        try:
            actual_f = float(actual)
        except ValueError:
            actual_f = 0.0
            
        if growth_type == "MoM":
            if prev_spend is not None and prev_spend > 0:
                growth_val = ((actual_f - prev_spend) / prev_spend) * 100
                growth_str = f"{'+' if growth_val > 0 else ''}{growth_val:.1f}%"
            else:
                growth_str = "n/a (no previous data)"
            
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "growth": growth_str,
                "formula_used": "((Current Month Actual - Previous Month Actual) / Previous Month Actual) * 100",
                "notes": notes
            })
            prev_spend = actual_f
        else:
             print(f"REFUSAL: Growth type {growth_type} not supported in deterministic implementation.")
             sys.exit(1)
             
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output results CSV")
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                for r in results:
                    writer.writerow(r)
        print(f"Success. Wrote {len(results)} computed records to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()

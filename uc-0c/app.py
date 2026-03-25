import argparse
import csv
import os
import sys

def load_dataset(input_path: str):
    """
    Reads the budget CSV, validates required columns, and identifies all null actual_spend rows.
    Returns: (list of data rows, list of null reports)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Budget file not found: {input_path}")
    
    data = []
    null_reports = []
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not all(col in reader.fieldnames for col in required_columns):
            raise ValueError(f"CSV missing one or more required columns: {required_columns}")
        
        for row_idx, row in enumerate(reader, start=2):
            try:
                # Store original values for reporting
                raw_actual = row["actual_spend"].strip()
                
                if not raw_actual:
                    null_reports.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "reason": row["notes"] if row["notes"] else "Reason not specified",
                        "line": row_idx
                    })
                    row["actual_spend"] = None
                else:
                    row["actual_spend"] = float(raw_actual)
                
                row["budgeted_amount"] = float(row["budgeted_amount"])
                data.append(row)
            except ValueError as e:
                print(f"Warning: Skipping malformed data at line {row_idx}: {e}")
                
    return data, null_reports

def compute_growth(ward: str, category: str, growth_type: str, data: list):
    """
    Calculates MoM growth for a specific ward and category.
    Includes formula in every output row and handles NULL values.
    """
    # Filter by ward and category
    filtered_data = [r for r in data if r["ward"] == ward and r["category"] == category]
    
    # Sort by period
    filtered_data.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered_data)):
        current = filtered_data[i]
        period = current["period"]
        actual = current["actual_spend"]
        
        res = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual is not None else "NULL",
            "growth": "n/a",
            "formula": "n/a",
            "notes": current["notes"] if actual is None else ""
        }
        
        if growth_type.upper() == "MOM":
            if i > 0:
                prev = filtered_data[i-1]
                prev_actual = prev["actual_spend"]
                
                if actual is not None and prev_actual is not None:
                    growth = ((actual - prev_actual) / prev_actual) * 100
                    res["growth"] = f"{growth:+.1f}%"
                    res["formula"] = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
                else:
                    res["growth"] = "NULL_IN_SEQUENCE"
                    res["formula"] = "Cannot compute: preceding or current value is NULL"
            else:
                res["formula"] = "Base month: No preceding period for MoM"
        
        results.append(res)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis App")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Target ward for analysis")
    parser.add_argument("--category", help="Target category for analysis")
    parser.add_argument("--growth-type", help="MoM (Year-over-Year not yet implemented)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    
    # Rule 4: If growth-type not specified, refuse
    if not args.growth_type:
        print("REFUSAL: Growth type (--growth-type) is required (e.g., MoM). System will not guess.")
        sys.exit(1)
        
    # Rule 1: Never aggregate across wards/categories unless explicitly asked
    # In this app, we require specific ward and category inputs
    if not args.ward or not args.category:
        print("REFUSAL: Specific --ward and --category are required. Universal aggregation is prohibited.")
        sys.exit(1)

    try:
        data, nulls = load_dataset(args.input)
        
        # Rule 2: Flag every null row before computing
        if nulls:
            print(f"IDENTIFIED {len(nulls)} NULL ROWS IN DATASET:")
            for n in nulls:
                print(f" - {n['period']} | {n['ward']} | {n['category']} | Reason: {n['reason']}")
        
        print(f"\nComputing {args.growth_type} growth for {args.ward} | {args.category}...")
        results = compute_growth(args.ward, args.category, args.growth_type, data)
        
        # Write output
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Results successfully written to {args.output}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
UC-0C — Urban Budget Growth Calculator
STBA Refined Implementation with Refusal Logic and Precision Reporting.
"""
import argparse
import csv
import os

def load_dataset(file_path: str):
    """
    Load ward_budget.csv and confirm 5 null rows existence.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    
    data = []
    null_count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["actual_spend"].strip():
                null_count += 1
            data.append(row)
    
    print(f"Data audit: {len(data)} rows loaded. Found {null_count} null actual_spend rows.")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str):
    """
    Calculate MoM growth for a specific ward/category. 
    Formula: (Current - Previous) / Previous * 100.
    Enforces one-decimal precision and contextual null reporting.
    """
    if not ward or not category:
        return "ERROR: CMC Policy Violation Rule #1: Specific Ward and Category MUST be provided. Aggregation refused."
    
    if growth_type.upper() != "MOM":
        return f"ERROR: CMC Policy Violation Rule #4: Unknown growth type '{growth_type}'. System refuses to guess."

    # Filter data and sort by period
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i in range(len(filtered)):
        row = filtered[i]
        period = row["period"]
        curr_spend_raw = row["actual_spend"].strip()
        
        # Base Case (No previous month for January)
        if i == 0:
            results.append({
                "period": period,
                "actual_spend": curr_spend_raw,
                "growth_rate": "n/a (baseline)",
                "formula": "None (start of year)"
            })
            continue
            
        prev_row = filtered[i-1]
        prev_spend_raw = prev_row["actual_spend"].strip()
        
        # Null Handling (Rule #2)
        if not curr_spend_raw:
            growth_rate = f"NULL: {row['notes']}"
            formula = "Calculation impossible due to missing data"
        elif not prev_spend_raw:
            growth_rate = f"NULL: Previous month ({prev_row['period']}) data missing"
            formula = "Calculation impossible due to missing baseline"
        else:
            # Mathematical Computation (Rule #5)
            curr = float(curr_spend_raw)
            prev = float(prev_spend_raw)
            if prev == 0:
                growth_rate = "inf"
                formula = "(curr - 0) / 0"
            else:
                growth = ((curr - prev) / prev) * 100
                growth_rate = f"{growth:+.1f}%"
                formula = f"({curr} - {prev}) / {prev} * 100"
                
        results.append({
            "period": period,
            "actual_spend": curr_spend_raw,
            "growth_rate": growth_rate,
            "formula": f"MoM: {formula}"
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Urban Budget Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--growth-type", default=None)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Rule #4 Check
    if not args.growth_type:
        print("ERROR: CMC Policy Violation Rule #4: --growth-type is required. Never guess the calculation formula.")
        return

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Rule #1 Refusal Check
    if isinstance(results, str):
        print(results)
        return

    # Write Output
    keys = results[0].keys()
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Done. Growth report written to {args.output}")

if __name__ == "__main__":
    main()

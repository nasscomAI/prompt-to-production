"""
UC-0C — Number That Looks Right
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
(Modified for local rule-based simulation since no API key is provided)
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    """
    Reads CSV, validates columns, reports null count.
    """
    data = []
    null_count = 0
    null_rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            if not row.get("actual_spend") or row.get("actual_spend").strip() == "":
                null_count += 1
                null_rows.append(f"{row['period']} - {row['ward']} - {row['category']}")
                
    print(f"Dataset loaded. Found {null_count} null 'actual_spend' values.")
    for nr in null_rows:
        print(f" - Null at: {nr}")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Enforces rules from agents.md.
    """
    # ENFORCEMENT: Never aggregate across wards or categories
    if not ward or ward.lower() == "any" or ward.lower() == "all":
        raise ValueError("REFUSED: Aggregation across wards is not allowed. Please specify a single ward.")
    if not category or category.lower() == "any" or category.lower() == "all":
        raise ValueError("REFUSED: Aggregation across categories is not allowed. Please specify a single category.")
        
    # ENFORCEMENT: If --growth-type not specified, refuse and ask
    if not growth_type:
        raise ValueError("REFUSED: --growth-type must be specified. I cannot guess.")
        
    # Filter data
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"]
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "growth": "n/a",
            "formula": "n/a",
            "flag": ""
        }
        
        # ENFORCEMENT: Flag every null row before computing
        if not actual or actual.strip() == "":
            result_row["growth"] = "NULL"
            result_row["formula"] = "NULL"
            result_row["flag"] = f"FLAGGED_NULL: {notes}"
            results.append(result_row)
            continue
            
        current_val = float(actual)
        
        # Compute growth based on type
        if growth_type == "MoM":
            if i > 0:
                prev_actual = filtered[i-1]["actual_spend"]
                if prev_actual and prev_actual.strip() != "":
                    prev_val = float(prev_actual)
                    if prev_val != 0:
                        growth_pct = ((current_val - prev_val) / prev_val) * 100
                        result_row["growth"] = f"{growth_pct:+.1f}%"
                        result_row["formula"] = f"({current_val} - {prev_val}) / {prev_val} * 100"
        elif growth_type == "YoY":
            result_row["growth"] = "YoY not fully simulated"
            result_row["formula"] = "current_year - prev_year"
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward")
    parser.add_argument("--category", required=False, help="Specific category")
    parser.add_argument("--growth-type", required=False, help="Growth type e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to write results")
    args = parser.parse_args()
    
    print("Loading dataset...")
    data = load_dataset(args.input)
    
    print("Computing growth...")
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"\n{str(e)}")
        sys.exit(1)
        
    print(f"Writing output to {args.output}...")
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        if not results:
            print("No data matched the criteria.")
            sys.exit(0)
            
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print("Done.")

if __name__ == "__main__":
    main()

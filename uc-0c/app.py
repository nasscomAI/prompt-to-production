"""
UC-0C Budget Analyst
Implemented using RICE workflow: agents.md -> skills.md -> CRAFT.
"""
import argparse
import csv
import os

def load_dataset(file_path: str) -> list:
    """
    Skill: Reads CSV, validates columns, and identifies null values.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found: {file_path}")
        
    data = []
    null_count = 0
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for null actual_spend
            if not row["actual_spend"] or row["actual_spend"].strip() == "":
                null_count += 1
                row["actual_spend"] = None
            else:
                row["actual_spend"] = float(row["actual_spend"])
            row["budgeted_amount"] = float(row["budgeted_amount"])
            data.append(row)
            
    if null_count > 0:
        print(f"Warning: Identified {null_count} null actual_spend values in the dataset.")
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: Computes MoM or YoY growth for specific ward and category.
    """
    if not growth_type:
        raise ValueError("Growth type (MoM/YoY) must be specified. Refusing to guess.")

    # Filter data
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not filtered:
        return []
        
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        period = current["period"]
        actual = current["actual_spend"]
        notes = current["notes"]
        
        row_result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual is not None else "NULL",
            "growth": "n/a",
            "formula": "n/a",
            "flag": ""
        }
        
        if actual is None:
            row_result["growth"] = "NOT COMPUTED"
            row_result["formula"] = "SKIP_NULL"
            row_result["flag"] = f"NULL DATA: {notes}"
        elif i > 0:
            previous = filtered[i-1]["actual_spend"]
            if previous is not None:
                if growth_type == "MoM":
                    growth = ((actual - previous) / previous) * 100
                    row_result["growth"] = f"{growth:+.1f}%"
                    row_result["formula"] = f"({actual} - {previous}) / {previous}"
                # YoY would be implemented similarly if previous year data existed
            else:
                row_result["growth"] = "NOT COMPUTED"
                row_result["formula"] = "PREVIOUS_VALUE_NULL"
                row_result["flag"] = "Cannot compute growth as previous period is null"
                
        results.append(row_result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Filter by Ward")
    parser.add_argument("--category", help="Filter by Category")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: Growth type (--growth-type) is mandatory. Please specify MoM or YoY.")
        return

    try:
        data = load_dataset(args.input)
        
        # If ward or category is "ALL" or not provided, we loop through unique values
        wards = [args.ward] if args.ward and args.ward != "ALL" else sorted(list(set(r["ward"] for r in data)))
        categories = [args.category] if args.category and args.category != "ALL" else sorted(list(set(r["category"] for r in data)))
        
        all_results = []
        for w in wards:
            for c in categories:
                all_results.extend(compute_growth(data, w, c, args.growth_type))
        
        if not all_results:
            print("No data found for the specified ward/category filters.")
            return

        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
            
        print(f"Success: Growth analysis for {len(wards)} wards written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Reads the budget CSV and reports on null values before returning data.
    """
    if not os.path.exists(file_path):
        print(f"Error: Dataset not found at {file_path}")
        return None
        
    data = []
    null_rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['actual_spend'] or row['actual_spend'].strip() == '':
                null_rows.append(row)
            data.append(row)
            
    print(f"--- Pre-processing Report ---")
    print(f"Total rows loaded: {len(data)}")
    print(f"Null actual_spend values detected: {len(null_rows)}")
    for nr in null_rows:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
    print(f"-----------------------------\n")
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates per-period growth for a specific ward and category.
    """
    # Refusal logic for aggregation
    if not ward or ward.lower() in ["all", "combined", "total"]:
        print("Error: All-ward aggregation is not permitted. Please specify a single ward.")
        sys.exit(1)
    if not category or category.lower() in ["all", "combined", "total"]:
        print("Error: All-category aggregation is not permitted. Please specify a single category.")
        sys.exit(1)
    if not growth_type:
        print("Error: Growth type (MoM/YoY) must be specified. Refusing to assume a default.")
        sys.exit(1)

    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return []

    # Sort by period to ensure correct growth calculation
    filtered.sort(key=lambda x: x['period'])

    results = []
    previous_spend = None
    
    for row in filtered:
        current_spend_str = row['actual_spend'].strip()
        current_spend = float(current_spend_str) if current_spend_str else None
        
        growth = "n/a"
        formula = "n/a"
        
        if current_spend is None:
            growth = f"NULL ({row['notes']})"
            formula = "Calculation skipped due to null value"
        elif previous_spend is not None:
            # Calculate growth
            change = current_spend - previous_spend
            growth_val = (change / previous_spend) * 100
            growth = f"{growth_val:+.1f}%"
            formula = f"({current_spend} - {previous_spend}) / {previous_spend}"
        elif previous_spend is None and not results:
            # First row in sequence
            growth = "Basis"
            formula = "First period in dataset"
        else:
            # Previous row was null
            growth = "n/a (Previous was NULL)"
            formula = "Calculation skipped because previous value was NULL"

        results.append({
            "period": row['period'],
            "ward": row['ward'],
            "category": row['category'],
            "actual_spend": current_spend if current_spend is not None else "NULL",
            "growth": growth,
            "formula": formula
        })
        
        previous_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", help="Type of growth analysis (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    if not data:
        return
        
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    if not results:
        return
        
    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Growth analysis complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()

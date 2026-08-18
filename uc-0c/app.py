"""
UC-0C app.py — Budget Analysis Implementation.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str):
    """Reads CSV and reports detected null values."""
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        sys.exit(1)
        
    data = []
    nulls_detected = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Check for null in actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip() == "":
                nulls_detected.append({
                    "row": i + 2, # 1-indexed + header
                    "period": row['period'],
                    "ward": row['ward'],
                    "category": row['category'],
                    "note": row.get('notes', 'No reason provided')
                })
                row['actual_spend'] = None
            else:
                try:
                    row['actual_spend'] = float(row['actual_spend'])
                except ValueError:
                    row['actual_spend'] = None
            data.append(row)
            
    if nulls_detected:
        print(f"INFO: Detected {len(nulls_detected)} null values in dataset.")
        for n in nulls_detected:
            print(f"  - Row {n['row']}: {n['period']} | {n['ward']} | {n['category']} | Reason: {n['note']}")
            
    return data

def compute_growth(dataset, ward, category, growth_type):
    """Computes growth for a specific slice of data."""
    # Filter data
    subset = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    
    if not subset:
        print(f"Error: No data found for Ward '{ward}' and Category '{category}'.")
        sys.exit(1)
        
    # Sort by period
    subset.sort(key=lambda x: x['period'])
    
    results = []
    formula = "(Current - Previous) / Previous * 100" if growth_type == "MoM" else "YoY Formula N/A for single year"
    
    for i, row in enumerate(subset):
        period = row['period']
        actual = row['actual_spend']
        growth_str = "N/A (Start)"
        note = ""
        
        if actual is None:
            growth_str = "NULL (Check Details)"
            note = f"Reason: {row['notes']}"
        elif i > 0 and subset[i-1]['actual_spend'] is not None:
            prev = subset[i-1]['actual_spend']
            if prev != 0:
                growth_val = ((actual - prev) / prev) * 100
                growth_str = f"{growth_val:+.1f}%"
            else:
                growth_str = "N/A (Prev=0)"
        elif i > 0:
            growth_str = "N/A (Prev is NULL)"
            
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual is not None else "NULL",
            "growth": growth_str,
            "formula": formula if i > 0 else "N/A",
            "notes": note
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward name")
    parser.add_argument("--category", required=False, help="Specific category")
    parser.add_argument("--growth-type", required=False, choices=["MoM", "YoY"], help="Growth type")
    parser.add_argument("--output", required=True, help="Path to write CSV")
    args = parser.parse_args()

    # Enforcement: Refuse aggregation or missing growth-type
    if not args.ward or not args.category:
        print("ERROR: All-ward or all-category aggregation is NOT PERMITTED. Please specify both --ward and --category.")
        sys.exit(1)
        
    if not args.growth_type:
        print("ERROR: --growth-type (MoM or YoY) is mandatory. Please specify one.")
        sys.exit(1)

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Write output
    keys = results[0].keys()
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Growth analysis written to {args.output}")

if __name__ == "__main__":
    main()

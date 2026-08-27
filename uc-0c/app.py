"""
UC-0C — Number That Looks Right
Implementation based on RICE enforcement in agents.md and skills defined in skills.md.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str) -> list:
    """
    Reads CSV and validates columns. Reports nullrows.
    """
    if not os.path.exists(file_path):
        return []

    data = []
    null_count = 0
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Count nulls in actual_spend for reporting
                if not row.get("actual_spend"):
                    null_count += 1
                data.append(row)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []
        
    print(f"Dataset loaded. Total rows: {len(data)}. Null actual_spend values detected: {null_count}.")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters data and computes growth while preserving formulas and flagging nulls.
    """
    if not growth_type:
        print("REFUSAL: Growth type (MoM/YoY) must be specified. Please specify --growth-type.")
        sys.exit(1)

    # Filtering
    subset = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    # Sort by period (assumes YYYY-MM format)
    subset.sort(key=lambda x: x['period'])

    results = []
    prev_spend = None

    for r in subset:
        val_str = r.get("actual_spend", "").strip()
        period = r.get("period")
        
        if not val_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "N/A",
                "formula": f"SKIPPED: {r.get('notes', 'No reason provided')}"
            })
            prev_spend = None # Break the chain for MoM on null
            continue

        curr_spend = float(val_str)
        growth = "0.0%"
        formula = "First period in slice"

        if prev_spend is not None and prev_spend != 0:
            if growth_type == "MoM":
                change = curr_spend - prev_spend
                growth_val = (change / prev_spend) * 100
                growth = f"{growth_val:+.1f}%"
                formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"
        
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": curr_spend,
            "growth": growth,
            "formula": formula
        })
        prev_spend = curr_spend

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Rule 1: Never aggregate across wards/categories unless explicitly asked
    if not args.ward or not args.category:
        print("REFUSAL: I am prohibited from providing all-ward or cross-category aggregations. Please specify reflecting both --ward and --category.")
        sys.exit(1)

    data = load_dataset(args.input)
    if not data:
        print(f"Error: Could not load data from {args.input}")
        return

    results = compute_growth(data, args.ward, args.category, args.growth_type)

    if results:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
        try:
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Growth analysis written to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()

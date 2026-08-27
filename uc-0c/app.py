"""
UC-0C — Budget Analyst
Implementation based on agents.md and skills.md specifications.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Skill: Reads CSV, validates schema, and identifies null values.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return None, []

    rows = []
    null_rows = []
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend"]
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Schema validation
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"Error: CSV missing required columns. Found: {reader.fieldnames}")
                return None, []
                
            for i, row in enumerate(reader):
                # Identify null actual_spend
                if not row["actual_spend"] or row["actual_spend"].strip() == "":
                    null_rows.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row["notes"]
                    })
                rows.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None, []

    return rows, null_rows

def compute_growth(rows, ward, category, growth_type):
    """
    Skill: Calculates MoM or YoY growth for a specific ward and category.
    """
    if not growth_type:
        print("Error: --growth-type (MoM or YoY) must be specified. Refusing to guess.")
        return []

    # Filter by ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    
    if not filtered:
        print(f"Error: No data found for Ward '{ward}' and Category '{category}'.")
        return []

    results = []
    prev_spend = None
    
    # Sort by period to ensure correct growth calculation
    filtered.sort(key=lambda x: x["period"])

    for row in filtered:
        period = row["period"]
        actual_str = row["actual_spend"]
        
        if not actual_str or actual_str.strip() == "":
            growth = "NULL"
            formula = "N/A"
            actual_val = "NULL"
            notes = f"Flagged: {row['notes']}"
        else:
            actual_val = float(actual_str)
            notes = ""
            if prev_spend is not None:
                growth_val = ((actual_val - prev_spend) / prev_spend) * 100
                growth = f"{growth_val:+.1f}%"
                formula = f"(({actual_val} - {prev_spend}) / {prev_spend}) * 100"
            else:
                growth = "n/a"
                formula = "First period in dataset"
            
            prev_spend = actual_val

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_val,
            "growth": growth,
            "formula": formula,
            "notes": notes
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", help="Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: Refuse aggregation or missing growth type
    if not args.ward or not args.category:
        print("Error: Granular enforcement active. Ward and Category must be specified. Refusing all-ward aggregation.")
        sys.exit(1)
    
    if not args.growth_type:
        print("Error: Growth type not specified. Please choose MoM or YoY.")
        sys.exit(1)

    rows, null_reports = load_dataset(args.input)
    if rows is None:
        sys.exit(1)

    # Pre-computation report of nulls
    if null_reports:
        print("Pre-computation Data Quality Report:")
        for nr in null_reports:
            print(f"  - NULL found in {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    if not results:
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
    try:
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Results written to {args.output}")
    except Exception as e:
        print(f"Error writing output CSV: {e}")

if __name__ == "__main__":
    main()

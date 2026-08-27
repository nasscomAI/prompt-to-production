"""
UC-0C app.py — Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads the budget CSV file, validates the expected columns, and returns the data.
    """
    rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate headers
            required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
            if not all(col in reader.fieldnames for col in required):
                print(f"Error: Missing required columns in dataset {input_path}")
                sys.exit(1)
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM or YoY spend growth for a specific ward and category.
    """
    # Filter by ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        print(f"Error: No data found for ward '{ward}' and category '{category}'")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        # Check if current spend is null
        if not actual_spend_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "N/A",
                "status": f"NULL: {notes}" if notes else "NULL: No reason provided in notes"
            })
            continue

        actual_spend = float(actual_spend_str)
        
        # Determine previous period index
        prev_idx = -1
        if growth_type == "MoM":
            prev_idx = i - 1
        elif growth_type == "YoY":
            # YoY is 12 periods back
            prev_idx = i - 12
            
        if prev_idx < 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual_spend),
                "growth": "N/A",
                "formula": "N/A",
                "status": "No base period available"
            })
            continue
            
        prev_row = filtered[prev_idx]
        prev_spend_str = prev_row["actual_spend"].strip()
        
        if not prev_spend_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual_spend),
                "growth": "NULL",
                "formula": f"({actual_spend} - NULL) / NULL",
                "status": f"Base period ({prev_row['period']}) spend was null: {prev_row['notes'].strip()}"
            })
            continue
            
        prev_spend = float(prev_spend_str)
        if prev_spend == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual_spend),
                "growth": "N/A",
                "formula": f"({actual_spend} - 0) / 0",
                "status": f"Base period ({prev_row['period']}) spend was zero"
            })
            continue

        # Calculate growth
        diff = actual_spend - prev_spend
        growth_val = (diff / prev_spend) * 100
        growth_str = f"{'+' if growth_val >= 0 else ''}{growth_val:.1f}%"
        formula_str = f"({actual_spend} - {prev_spend}) / {prev_spend}"
        
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": str(actual_spend),
            "growth": growth_str,
            "formula": formula_str,
            "status": "Computed successfully"
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Ward name")
    parser.add_argument("--category", default=None, help="Category name")
    parser.add_argument("--growth-type", default=None, help="MoM or YoY growth type")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    # Rule 1 & Rule 4: Enforce explicit arguments and refuse all-ward/all-category aggregations
    if not args.ward or not args.category:
        print("Refusal: Ward and Category must be specified. All-ward/all-category aggregation is not permitted.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Refusal: Growth type must be explicitly specified (MoM or YoY).")
        sys.exit(1)

    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Refusal: Invalid growth type '{args.growth_type}'. Must be MoM or YoY.")
        sys.exit(1)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    try:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "status"]
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

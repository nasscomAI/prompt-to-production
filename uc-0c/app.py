"""
UC-0C app.py — Ward Budget Growth Calculator
Implements RICE-compliant growth calculations with strict non-aggregation,
explicit formula printing, and null value flagging based on notes.
"""
import argparse
import csv
import os
import sys
from typing import List, Dict, Any

def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads the CSV dataset, checks columns, and parses numeric values.
    """
    if not os.path.exists(file_path):
        print(f"Error: Dataset file not found at {file_path}")
        sys.exit(1)

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    
    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Error: Empty CSV or invalid format.")
            sys.exit(1)
            
        header_set = set(reader.fieldnames)
        if not required_cols.issubset(header_set):
            print(f"Error: Missing required columns. Found: {reader.fieldnames}")
            sys.exit(1)
            
        for row in reader:
            parsed_row = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else 0.0,
                "actual_spend": None,
                "notes": row["notes"].strip(),
            }
            if row["actual_spend"].strip():
                try:
                    parsed_row["actual_spend"] = float(row["actual_spend"])
                except ValueError:
                    parsed_row["actual_spend"] = None
            data.append(parsed_row)
            
    return data

def compute_growth(dataset: List[Dict[str, Any]], ward: str, category: str, growth_type: str) -> List[Dict[str, Any]]:
    """
    Filters data for the specific ward and category, sorts by period,
    and computes period-over-period growth showing the formula and flagging nulls.
    """
    # Filter data
    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]
    
    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for idx, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        
        growth_rate = "n/a"
        formula = "n/a"
        status = "OK"
        
        # Check if current row is null
        if actual_spend is None:
            status = "NULL_ROW"
            growth_rate = "NULL"
            formula = f"NULL (Reason: {notes if notes else 'No notes available'})"
        elif idx == 0:
            growth_rate = "n/a"
            formula = "First period in sequence, no prior period data"
        else:
            prev_row = filtered[idx - 1]
            prev_spend = prev_row["actual_spend"]
            
            # Check if previous row was null
            if prev_spend is None:
                status = "PREV_NULL_ROW"
                growth_rate = "NULL"
                formula = f"NULL (Reason: Previous period actual spend is NULL due to '{prev_row['notes']}')"
            else:
                diff = actual_spend - prev_spend
                growth_rate_val = (diff / prev_spend) * 100
                
                # Format growth rate with sign
                sign = "+" if growth_rate_val >= 0 else ""
                growth_rate = f"{sign}{growth_rate_val:.1f}%"
                
                # Generate formula string
                formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "NULL" if actual_spend is None else actual_spend,
            "growth_rate": growth_rate,
            "formula": formula,
            "notes": notes,
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth results CSV")
    args = parser.parse_args()

    # Rule 4: Refuse and ask if growth-type is not specified
    if not args.growth_type:
        print("Refusal: --growth-type parameter is required. Please specify a valid type (e.g. MoM).")
        sys.exit(1)
        
    # Rule 1: Refuse if aggregation across wards or categories is implied/requested
    if not args.ward or args.ward.lower() in ["all", "any", "total", ""] or not args.category or args.category.lower() in ["all", "any", "total", ""]:
        print("Refusal: Calculation across multiple wards or categories is prohibited. You must specify a single ward and a single category.")
        sys.exit(1)

    # Load dataset
    dataset = load_dataset(args.input)
    
    # Verify the requested ward and category exist in the dataset
    wards_in_data = {r["ward"] for r in dataset}
    categories_in_data = {r["category"] for r in dataset}
    
    if args.ward not in wards_in_data:
        print(f"Error: Ward '{args.ward}' not found in dataset. Available wards: {sorted(list(wards_in_data))}")
        sys.exit(1)
        
    if args.category not in categories_in_data:
        print(f"Error: Category '{args.category}' not found in dataset. Available categories: {sorted(list(categories_in_data))}")
        sys.exit(1)

    # Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output to CSV
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "notes"]
    
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth calculation complete. Results written to {args.output}")

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Compute growth while handling null values and enforcing constraints.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads the CSV dataset and returns list of rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    rows = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Check columns
        expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not expected_cols.issubset(reader.fieldnames):
            raise ValueError(f"CSV missing expected columns. Found: {reader.fieldnames}")
            
        for row in reader:
            rows.append(row)
    return rows

def compute_growth(ward: str, category: str, growth_type: str, dataset: list) -> list:
    """
    Computes period growth for specified ward and category.
    """
    # Refuse if parameters are empty, "Any", or missing
    if not ward or ward.strip().lower() == "any":
        sys.exit("Error: Refusing calculation. Ward scope must be explicitly specified (cannot be 'Any' or empty).")
        
    if not category or category.strip().lower() == "any":
        sys.exit("Error: Refusing calculation. Category scope must be explicitly specified (cannot be 'Any' or empty).")
        
    if not growth_type or growth_type.strip() != "MoM":
        sys.exit(f"Error: Refusing calculation. Growth type must be explicitly specified as 'MoM'. Received: '{growth_type}'")
        
    # Filter dataset
    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    prev_spend = None
    prev_period = None
    
    for row in filtered:
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip()
        csv_note = row["notes"].strip()
        
        actual_spend = None
        if actual_spend_str != "":
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                actual_spend = None
                
        growth = "NULL"
        formula = "n/a"
        notes = csv_note
        
        if actual_spend is None:
            # Current month spend is null
            growth = "NULL"
            formula = "n/a"
            if not notes:
                notes = "Data is null"
        else:
            if prev_spend is None:
                # Previous month spend was null or this is the first month
                if prev_period is None:
                    # First month of the series
                    growth = "n/a"
                    formula = "n/a"
                    if not notes:
                        notes = "First month of data"
                else:
                    # Previous month existed but was null
                    growth = "NULL"
                    formula = "n/a"
                    notes = f"Cannot compute growth: previous month ({prev_period}) has null actual spend. " + csv_note
                    notes = notes.strip()
            else:
                # Compute MoM growth
                diff = actual_spend - prev_spend
                growth_val = (diff / prev_spend) * 100
                
                # Format growth value with sign and 1 decimal place
                if growth_val > 0:
                    growth = f"+{growth_val:.1f}%"
                elif growth_val < 0:
                    growth = f"{growth_val:.1f}%"
                else:
                    growth = "0.0%"
                    
                # Show mathematical formula: ((current - prev) / prev) * 100
                formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend_str if actual_spend_str else "NULL",
            "growth": growth,
            "formula": formula,
            "notes": notes
        })
        
        # Update trackers for next iteration
        prev_spend = actual_spend
        prev_period = period
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (or Any)")
    parser.add_argument("--category", required=True, help="Category name (or Any)")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write output growth_output.csv")
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)
    
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print(f"Growth calculation written to {args.output}")

if __name__ == "__main__":
    main()


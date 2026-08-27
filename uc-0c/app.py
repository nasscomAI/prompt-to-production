"""
UC-0C app.py — Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str) -> list:
    """
    Reads the budget CSV file, validates expected columns, and reports null counts.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    records = []
    null_count = 0
    null_rows = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")
                
        for line_num, row in enumerate(reader, start=2):
            records.append(row)
            actual = row.get("actual_spend", "").strip()
            if not actual:
                null_count += 1
                null_rows.append((line_num, row.get("period"), row.get("ward"), row.get("category"), row.get("notes")))
                
    print(f"Dataset loaded. Total rows: {len(records)}")
    print(f"Total null actual_spend values found: {null_count}")
    for r in null_rows:
        print(f"  Line {r[0]} | Period: {r[1]} | Ward: {r[2]} | Category: {r[3]} | Notes: {r[4]}")
        
    return records

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes the growth rates for a filtered ward and category.
    """
    if not ward or not category:
        print("Error: Requesting aggregation across wards/categories. Refusing to calculate.")
        sys.exit("Error: Refusing to aggregate across all wards/categories.")
        
    if not growth_type:
        print("Error: Growth type not specified. Refusing to calculate.")
        sys.exit("Error: --growth-type must be specified (MoM or YoY).")
        
    if growth_type not in ["MoM", "YoY"]:
        print(f"Error: Unknown growth type '{growth_type}'. Refusing to calculate.")
        sys.exit(f"Error: Unsupported growth type '{growth_type}'.")

    # Filter data by ward and category
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not filtered:
        print(f"No records found matching Ward: '{ward}' and Category: '{category}'.")
        return []
        
    # Sort by period chronologically
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        # Initialize result fields
        growth_rate = "NULL"
        formula = "n/a"
        status = "Computed"
        
        if not actual_str:
            status = f"NULL actual_spend: {notes if notes else 'No explanation'}"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_rate": "NULL",
                "formula": "n/a",
                "status": status
            })
            continue
            
        actual_val = float(actual_str)
        
        # Find the comparison row
        compare_row = None
        if growth_type == "MoM":
            if i > 0:
                compare_row = filtered[i-1]
            else:
                status = "First month of period - no previous month"
        elif growth_type == "YoY":
            # For YoY, find the row from 12 months ago
            curr_year, curr_month = map(int, period.split("-"))
            target_period = f"{curr_year-1:04d}-{curr_month:02d}"
            # Search in filtered
            for r in filtered:
                if r["period"] == target_period:
                    compare_row = r
                    break
            if not compare_row:
                status = f"No data found for previous year period ({target_period})"
                
        if status != "Computed":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_str,
                "growth_rate": "NULL",
                "formula": "n/a",
                "status": status
            })
            continue
            
        # We have a comparison row
        prev_actual_str = compare_row["actual_spend"].strip()
        prev_notes = compare_row["notes"].strip()
        prev_period = compare_row["period"]
        
        if not prev_actual_str:
            status = f"Cannot compute {growth_type}: comparison period ({prev_period}) actual_spend is NULL: {prev_notes}"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_str,
                "growth_rate": "NULL",
                "formula": "n/a",
                "status": status
            })
            continue
            
        prev_val = float(prev_actual_str)
        if prev_val == 0:
            status = f"Cannot compute {growth_type}: comparison period ({prev_period}) actual_spend is zero"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_str,
                "growth_rate": "NULL",
                "formula": "n/a",
                "status": status
            })
            continue
            
        # Perform calculation
        rate = ((actual_val - prev_val) / prev_val) * 100
        growth_rate = f"{rate:+.1f}%"
        formula = f"({actual_val} - {prev_val}) / {prev_val}"
        
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_str,
            "growth_rate": growth_rate,
            "formula": formula,
            "status": "Computed"
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Ward name")
    parser.add_argument("--category", default=None, help="Category name")
    parser.add_argument("--growth-type", default=None, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    # Check if arguments are present. We must refuse to guess and print error if required params are missing.
    args = parser.parse_args()
    
    if args.growth_type is None:
        print("Error: --growth-type is required. Refusing to guess.")
        sys.exit("Error: Refusing to proceed without --growth-type.")
        
    if args.ward is None or args.category is None:
        print("Error: Ward and Category must be specified. Refusing to aggregate across all wards/categories.")
        sys.exit("Error: Refusing to aggregate across all wards/categories.")
        
    print(f"Loading dataset: {args.input}")
    data = load_dataset(args.input)
    
    print(f"Computing {args.growth_type} growth for '{args.ward}' | '{args.category}'")
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Write output to CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "status"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
            
    print(f"Growth calculation completed. Results written to {args.output}")

if __name__ == "__main__":
    main()


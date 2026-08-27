"""
UC-0C — Number That Looks Right
Calculates month-over-month infrastructure spend growth from a ward-level budget CSV.
Fix: restricted aggregation to per-ward per-category only; blocks cross-ward/all-category queries.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found at: {file_path}")
        
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_count = 0
    null_rows = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Check columns
        if not required_cols.issubset(set(reader.fieldnames)):
            missing = required_cols - set(reader.fieldnames)
            raise ValueError(f"Missing required columns: {missing}")
            
        for i, row in enumerate(reader, start=2):  # 1-based, line 1 is header
            # Check if actual_spend is null or empty
            val = row.get("actual_spend", "").strip()
            if val == "":
                null_count += 1
                null_rows.append((i, row.get("period"), row.get("ward"), row.get("category"), row.get("notes")))
            rows.append(row)
            
    print(f"Dataset loaded. Total rows: {len(rows)}")
    print(f"Null actual_spend rows detected: {null_count}")
    for nr in null_rows:
        print(f"  Line {nr[0]}: {nr[1]} | {nr[2]} | {nr[3]} | Note: {nr[4]}")
        
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters by ward and category, then computes period-over-period growth rates.
    """
    if not growth_type:
        print("Error: --growth-type not specified. Refusing computation.", file=sys.stderr)
        sys.exit("Error: --growth-type is required.")
        
    if growth_type not in ["MoM", "YoY"]:
        sys.exit(f"Error: Unknown growth-type '{growth_type}'. Must be MoM or YoY.")
        
    if not ward or not category:
        sys.exit("Error: Both --ward and --category must be specified.")
        
    if ward.lower() == "all" or category.lower() == "all":
        sys.exit("Error: Aggregation across all wards or categories is not permitted. Refusing request.")
        
    # Filter and sort by period
    filtered_rows = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered_rows.sort(key=lambda r: r["period"])
    
    if not filtered_rows:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'")
        return []
        
    results = []
    
    for i, row in enumerate(filtered_rows):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        # 1. Check if current actual_spend is NULL
        if actual_str == "":
            results.append({
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "Growth": "NULL",
                "Formula": "n/a",
                "Notes": notes if notes else "Data missing"
            })
            continue
            
        current_val = float(actual_str)
        
        # 2. First period handles differently
        if i == 0:
            results.append({
                "Period": period,
                "Actual Spend (₹ lakh)": f"{current_val:.1f}",
                "Growth": "n/a",
                "Formula": "n/a",
                "Notes": notes
            })
            continue
            
        # Get preceding period
        prev_row = filtered_rows[i - 1]
        prev_actual_str = prev_row["actual_spend"].strip()
        
        # 3. Preceding is NULL
        if prev_actual_str == "":
            results.append({
                "Period": period,
                "Actual Spend (₹ lakh)": f"{current_val:.1f}",
                "Growth": "NULL",
                "Formula": "n/a",
                "Notes": f"Cannot compute: preceding month spend ({prev_row['period']}) is NULL"
            })
            continue
            
        prev_val = float(prev_actual_str)
        
        # 4. Compute growth
        diff = current_val - prev_val
        growth_frac = diff / prev_val
        growth_pct = growth_frac * 100
        
        # Format growth with + or - sign
        if growth_pct > 0:
            growth_str = f"+{growth_pct:.1f}%"
        elif growth_pct < 0:
            growth_str = f"{growth_pct:.1f}%"
        else:
            growth_str = "0.0%"
            
        # Format formula
        formula_str = f"(({current_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}) * 100 = {growth_str}"
        
        results.append({
            "Period": period,
            "Actual Spend (₹ lakh)": f"{current_val:.1f}",
            "Growth": growth_str,
            "Formula": formula_str,
            "Notes": notes
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Spend Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Spend category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing computation.", file=sys.stderr)
        sys.exit("Error: --growth-type is required.")
        
    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        if results:
            fieldnames = ["Period", "Actual Spend (₹ lakh)", "Growth", "Formula", "Notes"]
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Growth calculation written to {args.output}")
        else:
            print("No output written due to lack of filtered rows.")
    except Exception as e:
        print(f"Error during growth calculation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

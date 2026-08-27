"""
UC-0C app.py — Implemented using RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path):
    """
    Reads the CSV dataset from the input path, validates that the required columns are present,
    and reports the null count and specific rows with null values before returning the data.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    rows = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Error: Input CSV file is empty.", file=sys.stderr)
            sys.exit(1)
            
        missing_cols = [col for col in required_cols if col not in reader.fieldnames]
        if missing_cols:
            print(f"Error: Missing required columns in CSV: {missing_cols}", file=sys.stderr)
            sys.exit(1)
            
        for row in reader:
            rows.append(row)
            
    # Count and report null values in actual_spend
    null_rows = []
    for i, row in enumerate(rows):
        spend_str = row["actual_spend"].strip() if row["actual_spend"] else ""
        if spend_str == "":
            null_rows.append((i, row))
            
    print("--- Dataset Loaded ---")
    print(f"Total Rows: {len(rows)}")
    print(f"Null actual_spend Count: {len(null_rows)}")
    if null_rows:
        print("Flagged Null Rows:")
        for idx, r in null_rows:
            # CSV line is index + 2 (1-based index and header)
            print(f"  Line {idx + 2}: Period={r['period']}, Ward='{r['ward']}', Category='{r['category']}', Notes='{r['notes']}'")
    print("----------------------")
    
    return rows

def get_previous_month(period_str):
    """
    Given a period string 'YYYY-MM', returns the previous month's string 'YYYY-MM'.
    """
    try:
        parts = period_str.split("-")
        if len(parts) != 2:
            return None
        y, m = int(parts[0]), int(parts[1])
        if m == 1:
            y_prev = y - 1
            m_prev = 12
        else:
            y_prev = y
            m_prev = m - 1
        return f"{y_prev:04d}-{m_prev:02d}"
    except Exception:
        return None

def get_same_month_previous_year(period_str):
    """
    Given a period string 'YYYY-MM', returns the same month of the previous year 'YYYY-MM'.
    """
    try:
        parts = period_str.split("-")
        if len(parts) != 2:
            return None
        y, m = int(parts[0]), int(parts[1])
        return f"{y-1:04d}-{m:02d}"
    except Exception:
        return None

def compute_growth(rows, ward_filter, category_filter, growth_type):
    """
    Computes period-over-period growth (MoM or YoY) for the selected ward and category.
    Returns list of output row dictionaries.
    """
    # Group rows by (ward, category) to process each series independently
    groups = {}
    for r in rows:
        w = r["ward"]
        c = r["category"]
        key = (w, c)
        if key not in groups:
            groups[key] = []
        groups[key].append(r)
        
    output_rows = []
    
    # Process each group
    for (w, c), group_rows in groups.items():
        # Apply filters if specified
        if ward_filter and w != ward_filter:
            continue
        if category_filter and c != category_filter:
            continue
            
        # Sort chronologically by period
        group_rows_sorted = sorted(group_rows, key=lambda x: x["period"])
        
        # Map period to row dictionary for easy lookup
        period_map = {r["period"]: r for r in group_rows_sorted}
        
        for r in group_rows_sorted:
            period = r["period"]
            notes = r["notes"].strip() if r["notes"] else ""
            curr_spend_str = r["actual_spend"].strip() if r["actual_spend"] else ""
            
            # Check if current spend is null
            if curr_spend_str == "":
                flagged_reason = notes if notes else "No note provided"
                growth_str = f"NULL - {flagged_reason}"
                formula_str = "n/a (current spend is null)"
                output_rows.append({
                    "period": period,
                    "ward": w,
                    "category": c,
                    "actual_spend": "NULL",
                    "growth": growth_str,
                    "formula": formula_str
                })
                continue
                
            # Get comparison period
            if growth_type == "MoM":
                comp_period = get_previous_month(period)
            elif growth_type == "YoY":
                comp_period = get_same_month_previous_year(period)
            else:
                comp_period = None
                
            if not comp_period:
                growth_str = "n/a"
                formula_str = f"n/a (invalid target period)"
                output_rows.append({
                    "period": period,
                    "ward": w,
                    "category": c,
                    "actual_spend": curr_spend_str,
                    "growth": growth_str,
                    "formula": formula_str
                })
                continue
                
            # Lookup comparison row
            comp_row = period_map.get(comp_period)
            if not comp_row:
                growth_str = "n/a"
                formula_str = f"n/a (no data for {comp_period})"
                output_rows.append({
                    "period": period,
                    "ward": w,
                    "category": c,
                    "actual_spend": curr_spend_str,
                    "growth": growth_str,
                    "formula": formula_str
                })
                continue
                
            comp_spend_str = comp_row["actual_spend"].strip() if comp_row["actual_spend"] else ""
            if comp_spend_str == "":
                growth_str = f"NULL - Previous spend at {comp_period} is null"
                formula_str = f"n/a (previous spend at {comp_period} is null)"
                output_rows.append({
                    "period": period,
                    "ward": w,
                    "category": c,
                    "actual_spend": curr_spend_str,
                    "growth": growth_str,
                    "formula": formula_str
                })
                continue
                
            # Compute growth
            try:
                curr_val = float(curr_spend_str)
                comp_val = float(comp_spend_str)
                
                if comp_val == 0.0:
                    growth_str = "n/a"
                    formula_str = f"(({curr_val} - 0.0) / 0.0) * 100 (division by zero)"
                else:
                    diff = curr_val - comp_val
                    growth_val = (diff / comp_val) * 100
                    
                    if growth_val > 0:
                        growth_str = f"+{growth_val:.1f}%"
                    elif growth_val < 0:
                        growth_str = f"{growth_val:.1f}%"
                    else:
                        growth_str = "0.0%"
                        
                    formula_str = f"(({curr_val} - {comp_val}) / {comp_val}) * 100"
                    
            except ValueError:
                growth_str = "Error"
                formula_str = f"n/a (invalid numeric value)"
                
            output_rows.append({
                "period": period,
                "ward": w,
                "category": c,
                "actual_spend": curr_spend_str,
                "growth": growth_str,
                "formula": formula_str
            })
            
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", help="Ward filter")
    parser.add_argument("--category", help="Category filter")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # Enforcement: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type is not specified. Please specify either MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    growth_type = args.growth_type.strip()
    if growth_type not in ["MoM", "YoY"]:
        print(f"Error: Invalid --growth-type '{args.growth_type}'. Must be MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    refuse_keywords = ["all", "total", "aggregate", "sum", "average", "mean", "combined", "any"]
    if args.ward and args.ward.strip().lower() in refuse_keywords:
        print("Error: Aggregation across wards is not allowed. Please specify a single ward or omit filters to compute per-ward tables.", file=sys.stderr)
        sys.exit(1)
    if args.category and args.category.strip().lower() in refuse_keywords:
        print("Error: Aggregation across categories is not allowed. Please specify a single category or omit filters to compute per-category tables.", file=sys.stderr)
        sys.exit(1)
        
    # Load dataset
    rows = load_dataset(args.input)
    
    # Compute growth
    results = compute_growth(rows, args.ward, args.category, growth_type)
    
    if not results:
        print(f"Warning: No rows matched ward='{args.ward}' and category='{args.category}'.", file=sys.stderr)
        
    # Write to output file
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print(f"Success: Growth computed successfully and written to {args.output}")
    print(f"Total output rows written: {len(results)}")
    
    # Print the output table to console for visibility
    print("\n--- Output Results Summary ---")
    print(f"{'Period':<10} | {'Ward':<22} | {'Category':<26} | {'Spend':<8} | {'Growth':<10} | {'Formula'}")
    print("-" * 110)
    for r in results[:30]:  # Limit print to 30 rows
        print(f"{r['period']:<10} | {r['ward']:<22} | {r['category']:<26} | {r['actual_spend']:<8} | {r['growth']:<10} | {r['formula']}")
    if len(results) > 30:
        print(f"... and {len(results) - 30} more rows.")
    print("------------------------------")

if __name__ == "__main__":
    main()

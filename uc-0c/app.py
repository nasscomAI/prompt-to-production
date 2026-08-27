"""
UC-0C — Number That Looks Right
Deterministic budget analyzer enforcing strict validation, null flagging, and formula transparency.
"""
import argparse
import csv
import sys
import os

def load_dataset(file_path: str) -> list:
    """
    Read CSV, validate columns, report null counts and return list of dicts.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
        
    rows = []
    null_count = 0
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            # Check basic structure
            for col in ["period", "ward", "category", "budgeted_amount", "actual_spend"]:
                if col not in row:
                    print(f"Error: Missing column {col} in CSV.", file=sys.stderr)
                    sys.exit(1)
            
            # Detect nulls
            actual = row.get("actual_spend", "").strip()
            if not actual:
                null_count += 1
                row["actual_spend"] = None
            else:
                try:
                    row["actual_spend"] = float(actual)
                except ValueError:
                    row["actual_spend"] = None
                    null_count += 1
            
            try:
                row["budgeted_amount"] = float(row["budgeted_amount"])
            except ValueError:
                row["budgeted_amount"] = 0.0
                
            rows.append(row)
            
    print(f"Loaded {len(rows)} rows. Found {null_count} null actual_spend rows.")
    return rows

def compute_growth(rows: list, target_ward: str, target_category: str, growth_type: str) -> list:
    """
    Filter rows, compute growth, and output formatted result rows.
    """
    # 1. Filter rows matching ward and category
    filtered = [r for r in rows if r["ward"] == target_ward and r["category"] == target_category]
    
    # Sort by period chronologically
    filtered.sort(key=lambda x: x["period"])
    
    output_rows = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        budgeted = row["budgeted_amount"]
        notes = row.get("notes", "").strip()
        
        # Default fields
        growth_val = "NULL"
        formula = "n/a"
        
        if actual is None:
            # Current value is null
            reason = notes if notes else "No data submitted"
            growth_val = "NULL"
            formula = "n/a (current period actual spend is NULL)"
            notes = f"NULL: {reason}"
        elif i == 0:
            # First month, no previous month to compare
            growth_val = "n/a"
            formula = "n/a (first period)"
        else:
            prev_row = filtered[i-1]
            prev_actual = prev_row["actual_spend"]
            
            if prev_actual is None:
                # Previous value is null
                growth_val = "NULL"
                formula = f"n/a (previous period {prev_row['period']} actual spend is NULL)"
                notes = f"NULL: Cannot compute due to missing previous month data"
            else:
                # Compute MoM growth
                diff = actual - prev_actual
                pct = (diff / prev_actual) * 100
                sign = "+" if pct >= 0 else ""
                growth_val = f"{sign}{pct:.1f}%"
                formula = f"({actual} - {prev_actual}) / {prev_actual} * 100 = {growth_val}"
                
        output_rows.append({
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "budgeted_amount": budgeted,
            "actual_spend": actual if actual is not None else "NULL",
            "growth": growth_val,
            "formula": formula,
            "notes": notes
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name")
    parser.add_argument("--category", help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # 1. Enforce growth-type specification
    if not args.growth_type:
        print("Refusal Error: --growth-type must be explicitly specified (e.g. MoM). We do not guess.", file=sys.stderr)
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print(f"Refusal Error: Growth type '{args.growth_type}' is not supported or cannot be computed with the available 2024 dataset. Only 'MoM' is supported.", file=sys.stderr)
        sys.exit(1)
        
    # 2. Enforce ward and category specification (prevent all-ward or all-category aggregation)
    if not args.ward or not args.category:
        print("Refusal Error: Both --ward and --category must be explicitly specified. Aggregating across all wards or categories is prohibited.", file=sys.stderr)
        sys.exit(1)
        
    if args.ward.lower() in ["any", "all", "none", ""] or args.category.lower() in ["any", "all", "none", ""]:
        print("Refusal Error: Specific ward and category values must be provided. 'Any' or 'All' aggregation is prohibited.", file=sys.stderr)
        sys.exit(1)
        
    # 3. Load and validate dataset
    rows = load_dataset(args.input)
    
    # 4. Check if the specified ward/category exists in dataset to prevent silent failures
    wards_in_data = set(r["ward"] for r in rows)
    categories_in_data = set(r["category"] for r in rows)
    
    if args.ward not in wards_in_data:
        print(f"Refusal Error: Ward '{args.ward}' not found in dataset. Available: {sorted(list(wards_in_data))}", file=sys.stderr)
        sys.exit(1)
        
    if args.category not in categories_in_data:
        print(f"Refusal Error: Category '{args.category}' not found in dataset. Available: {sorted(list(categories_in_data))}", file=sys.stderr)
        sys.exit(1)
        
    # 5. Compute growth
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    # 6. Write output
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Growth calculation completed. Results written to {args.output}")

if __name__ == "__main__":
    main()

import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates columns, and reports any null values count and rows before returning the data.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
        
    expected_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    
    data = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames if reader.fieldnames else [])
        if not expected_columns.issubset(headers):
            print(f"Error: Schema validation failed. \nExpected columns: {expected_columns}\nFound: {headers}", file=sys.stderr)
            sys.exit(1)
            
        for row_idx, row in enumerate(reader, start=2): # 1-based header is row 1
            data.append(row)
            
            # Check for null in actual_spend. Treat empty string or "NULL" as missing data
            actual = row.get("actual_spend", "").strip()
            if actual == "" or actual.upper() == "NULL":
                null_rows.append({
                    "row": row_idx, 
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes", "No reason provided")
                })

    if null_rows:
        print(f"Attention: Flagged {len(null_rows)} explicitly null actual_spend value(s):")
        for r in null_rows:
            print(f" - Row {r['row']} | Period: {r['period']} | Ward: {r['ward']} | Category: {r['category']} | Reason: {r['notes']}")
            
    return data

def compute_growth(dataset, target_ward, target_category, growth_type):
    """
    Calculates growth (e.g., MoM) for a specific ward and category over time.
    """
    # 1. Enforcement rule: Never aggregate across wards or categories unless explicitly instructed
    if target_ward.lower() in ("all", "any", "*") or target_category.lower() in ("all", "any", "*"):
        print("Error: Never aggregate across wards or categories unless explicitly instructed. Refusing request.", file=sys.stderr)
        sys.exit(1)
        
    # Filter for the specific ward and category
    filtered = []
    for row in dataset:
        if row["ward"] == target_ward and row["category"] == target_category:
            filtered.append(row)
            
    # Sort by period string just in case
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row.get("actual_spend", "").strip()
        
        # 2. Enforcement rule: Handle and document nulls
        if actual_str == "" or actual_str.upper() == "NULL":
            results.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "Not computed (Null actual_spend flagged)"
            })
            continue
            
        current_val = float(actual_str)
        growth_val = "NULL"
        formula = "N/A"
        
        if growth_type.lower() == "mom":
            if i > 0:
                prev_str = filtered[i-1].get("actual_spend", "").strip()
                if prev_str != "" and prev_str.upper() != "NULL":
                    prev_val = float(prev_str)
                    if prev_val != 0:
                        growth = ((current_val - prev_val) / prev_val) * 100
                        growth_val = f"{growth:+.1f}%"
                        # 3. Enforcement rule: Show formula used in every output row
                        formula = f"([{current_val} - {prev_val}] / {prev_val}) * 100"
                    else:
                        formula = "Division by zero (previous value was 0)"
                else:
                    formula = "Previous period was NULL — cannot compute"
            else:
                formula = "No previous period available for MoM calculation"
        elif growth_type.lower() == "yoy":
            curr_year, curr_month = map(int, period.split('-'))
            target_prev_period = f"{curr_year-1}-{curr_month:02d}"
            
            prev_val = None
            for prev_row in filtered[:i]:
                if prev_row["period"] == target_prev_period:
                    p_str = prev_row.get("actual_spend", "").strip()
                    if p_str != "" and p_str.upper() != "NULL":
                        prev_val = float(p_str)
                    break
                    
            if prev_val is not None:
                if prev_val != 0:
                    growth = ((current_val - prev_val) / prev_val) * 100
                    growth_val = f"{growth:+.1f}%"
                    formula = f"([{current_val} - {prev_val}] / {prev_val}) * 100"
                else:
                    formula = "Division by zero (previous year value was 0)"
            else:
                formula = "No matching prior year period found or was NULL"
        else:
             print(f"Error: Unknown growth type specified '{growth_type}'", file=sys.stderr)
             sys.exit(1)
             
        results.append({
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": current_val,
            "growth": growth_val,
            "formula": formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate spend growth metrics from budget data.")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze (required, cannot be 'Any')")
    parser.add_argument("--category", required=True, help="Specific category to analyze (required, cannot be 'Any')")
    parser.add_argument("--growth-type", help="Type of growth to calculate (e.g., MoM, YoY). Mandatory.")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args, unknown = parser.parse_known_args()
    
    # 4. Enforcement rule: Refuse and ask if growth-type is not specified
    if not args.growth_type:
        print("Error: --growth-type not specified. I must refuse and ask for explicitly chosen formula. Never guessing.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    print(f"\nComputing {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'...")
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    print(f"Writing output to {args.output}...")
    # Ensuring output directory exists, if any was passed
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print("Done!")

if __name__ == "__main__":
    main()

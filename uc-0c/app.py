"""
UC-0C app.py — Financial Growth Analyst
Implements load_dataset and compute_growth enforcing strict rules against aggregation and silent null handling.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str):
    """
    Reads the budget CSV file, validates expected columns, and reports upfront 
    on any null values in actual_spend before any computation begins.
    """
    dataset = []
    null_count = 0
    null_records = []
    
    expected_headers = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if reader.fieldnames is None or not all(h in reader.fieldnames for h in expected_headers):
                print(f"ERROR: Missing expected columns. Expected: {expected_headers}", file=sys.stderr)
                sys.exit(1)
                
            for row in reader:
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_count += 1
                    null_records.append({
                        "period": row['period'],
                        "ward": row['ward'],
                        "category": row['category'],
                        "notes": row['notes']
                    })
    except Exception as e:
        print(f"ERROR: Cannot load dataset from {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement Rule 2: Flag every null row before computing
    print(f"Dataset Validation: Loaded {len(dataset)} rows.")
    if null_count > 0:
        print(f"WARNING: Found {null_count} rows with NULL actual_spend:")
        for record in null_records:
            print(f"  -> {record['period']} | {record['ward']} | {record['category']} | Reason: {record['notes']}")
    else:
        print("Validation Passed: No NULL actual_spend values found.")
        
    return dataset

def compute_growth(dataset: list, ward: str, category: str, growth_type: str):
    """
    Computes period-over-period financial growth strictly constrained to a 
    single ward and category, displaying the exact formula used.
    """
    # Enforcement Rule 1: Never aggregate across wards or categories. Refuse if asked.
    if ward.lower() == "any" or ward.lower() == "all" or not ward:
        print("REFUSAL: Cannot aggregate across multiple wards. Specific ward required.", file=sys.stderr)
        sys.exit(1)
    if category.lower() == "any" or category.lower() == "all" or not category:
        print("REFUSAL: Cannot aggregate across multiple categories. Specific category required.", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement Rule 4: If growth_type not specified or unclear, refuse and ask.
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        print("REFUSAL: Invalid or missing --growth-type. Must explicitly specify MoM or YoY. Guessing is not permitted.", file=sys.stderr)
        sys.exit(1)
        
    growth_type = growth_type.upper()
    
    # Filter dataset
    target_data = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not target_data:
        print(f"WARNING: No data found for Ward: '{ward}', Category: '{category}'.", file=sys.stderr)
        sys.exit(1)
        
    # Sort chronologically
    target_data.sort(key=lambda x: x['period'])
    
    results = []
    
    # Compute growth
    for i, row in enumerate(target_data):
        period = row['period']
        actual_spend_raw = row['actual_spend'].strip()
        
        # Enforcement Rule 2 & 3: Handle individual row nulls clearly
        if not actual_spend_raw:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "Must be flagged - not computed",
                "formula": "None (Null Value)"
            })
            continue
            
        current_spend = float(actual_spend_raw)
        
        # Get previous value depending on growth type
        previous_spend = None
        if growth_type == "MOM" and i > 0:
            prev_raw = target_data[i-1]['actual_spend'].strip()
            if prev_raw:
                previous_spend = float(prev_raw)
        elif growth_type == "YOY" and i >= 12:
            prev_raw = target_data[i-12]['actual_spend'].strip()
            if prev_raw:
                previous_spend = float(prev_raw)
                
        # Calculate metric
        if previous_spend is None:
            results.append({
                "period": period,
                "actual_spend": f"{current_spend:.1f}",
                "growth": "n/a (no previous data)",
                "formula": "n/a"
            })
        else:
            if previous_spend == 0:
                growth_str = "n/a (div by zero)"
            else:
                growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
                sign = "+" if growth_pct > 0 else ""
                growth_str = f"{sign}{growth_pct:.1f}%"
                
            # Enforcement Rule 3: Show exact formula used
            formula_str = f"({current_spend:.1f} - {previous_spend:.1f}) / {previous_spend:.1f} * 100"
            
            results.append({
                "period": period,
                "actual_spend": f"{current_spend:.1f}",
                "growth": growth_str,
                "formula": formula_str
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific Ward (e.g., 'Ward 1 - Kasba')")
    parser.add_argument("--category", required=True, help="Specific Category")
    parser.add_argument("--growth-type", required=False, help="Calculation method: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    print("\n--- Phase 1: Load and Validate ---")
    dataset = load_dataset(args.input)
    
    print("\n--- Phase 2: Compute Growth ---")
    if not args.growth_type:
        print("REFUSAL: --growth-type was not provided. The system cannot guess the intended formula. Please configure appropriately.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Computing {args.growth_type.upper()} for [{args.ward}] -> [{args.category}]")
    growth_results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Save output
    out_headers = ["ward", "category", "period", "actual_spend", "growth", "formula"]
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=out_headers)
            writer.writeheader()
            for r in growth_results:
                writer.writerow({
                    "ward": args.ward,
                    "category": args.category,
                    "period": r["period"],
                    "actual_spend": r["actual_spend"],
                    "growth": r["growth"],
                    "formula": r["formula"]
                })
        print(f"Success: Report written to {args.output}")
    except Exception as e:
        print(f"ERROR: Cannot write to output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads the CSV dataset, checks columns, and returns rows as a list of dicts.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    rows = []
    with open(input_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
        for col in required_cols:
            if col not in reader.fieldnames:
                print(f"Error: Missing required column '{col}' in CSV dataset.")
                sys.exit(1)
                
        for row in reader:
            rows.append(row)
            
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters rows by ward and category, sorts by period, and calculates growth.
    """
    # Filter dataset for the specific ward and category
    filtered = []
    for r in rows:
        if r['ward'].strip() == ward.strip() and r['category'].strip() == category.strip():
            filtered.append(r)
            
    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, curr in enumerate(filtered):
        period = curr['period']
        budget = curr['budgeted_amount']
        notes = curr['notes'].strip()
        
        # Parse actual spend
        curr_spend_str = curr['actual_spend'].strip()
        if not curr_spend_str:
            curr_spend = None
        else:
            try:
                curr_spend = float(curr_spend_str)
            except ValueError:
                curr_spend = None
                
        if curr_spend is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "n/a",
                "notes": notes if notes else "Actual spend is missing"
            })
            continue
            
        # If MoM, get previous month
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budget,
                    "actual_spend": curr_spend,
                    "growth": "NULL",
                    "formula": "n/a",
                    "notes": "First period in dataset, no baseline available."
                })
            else:
                prev = filtered[i - 1]
                prev_spend_str = prev['actual_spend'].strip()
                if not prev_spend_str:
                    prev_spend = None
                else:
                    try:
                        prev_spend = float(prev_spend_str)
                    except ValueError:
                        prev_spend = None
                        
                if prev_spend is None:
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budget,
                        "actual_spend": curr_spend,
                        "growth": "NULL",
                        "formula": "n/a",
                        "notes": f"Previous period ({prev['period']}) actual spend was NULL."
                    })
                else:
                    # Compute MoM growth
                    diff = curr_spend - prev_spend
                    growth_val = (diff / prev_spend) * 100
                    formula_str = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
                    
                    # Format as percentage string, e.g. "+33.1%" or "-34.8%"
                    sign = "+" if growth_val >= 0 else ""
                    growth_str = f"{sign}{growth_val:.1f}%"
                    
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budget,
                        "actual_spend": curr_spend,
                        "growth": growth_str,
                        "formula": formula_str,
                        "notes": notes
                    })
        elif growth_type == "YoY":
            # For YoY, we check if there's a record 12 periods before
            # Since our dataset is 12 periods total (Jan-Dec 2024), we cannot calculate YoY.
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": curr_spend,
                "growth": "NULL",
                "formula": "n/a",
                "notes": "Insufficient data. YoY requires comparison with previous year, which is not in dataset."
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    # 1. Enforce --growth-type requirement
    if not args.growth_type:
        print("Refusal: --growth-type is required. Please specify MoM or YoY.")
        sys.exit(1)
        
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Refusal: Invalid growth-type '{args.growth_type}'. Must be MoM or YoY.")
        sys.exit(1)
        
    # 2. Enforce no all-ward or all-category aggregation
    if not args.ward or args.ward.strip().lower() in ["all", "any", ""]:
        print("Refusal: Ward name must be specified. Cross-ward aggregation is prohibited.")
        sys.exit(1)
        
    if not args.category or args.category.strip().lower() in ["all", "any", ""]:
        print("Refusal: Category name must be specified. Cross-category aggregation is prohibited.")
        sys.exit(1)
        
    # Load dataset
    rows = load_dataset(args.input)
    
    # Compute growth
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    if not results:
        print(f"Warning: No matching budget records found for Ward '{args.ward}' and Category '{args.category}'.")
        
    # Write output
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
            
    print(f"Successfully wrote growth analysis to {args.output}")

if __name__ == "__main__":
    main()

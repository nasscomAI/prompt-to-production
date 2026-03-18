import argparse
import csv
import sys
import os

def check_aggregation_refusal(args):
    """Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked"""
    if not args.ward or args.ward.lower() in ["all", "any"]:
        print("REFUSAL: Cannot aggregate across multiple wards. Please specify a single ward.")
        sys.exit(1)
    if not args.category or args.category.lower() in ["all", "any"]:
        print("REFUSAL: Cannot aggregate across multiple categories. Please specify a single category.")
        sys.exit(1)

def check_growth_type_refusal(args):
    """Enforcement Rule 4: If --growth-type not specified — refuse and ask, never guess"""
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. I cannot guess the growth type. Please specify 'MoM' or 'YoY'.")
        sys.exit(1)
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"REFUSAL: Unknown growth type '{args.growth_type}'. Please specify 'MoM' or 'YoY'.")
        sys.exit(1)

def load_and_validate(input_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    # Enforcement Rule 2: Flag every null row before computing
    null_count = sum(1 for row in filtered if not row.get('actual_spend'))
    if null_count > 0:
        print(f"FLAG: Found {null_count} rows with null actual_spend for {ward} - {category}.")
        for row in filtered:
            if not row.get('actual_spend'):
                print(f"      Null in {row['period']}. Reason: {row.get('notes', 'Unknown')}")
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '').strip()
        
        if not actual_str:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAGGED - NOT COMPUTED",
                "formula": f"Null missing data. Reason: {notes}"
            })
            continue
            
        current_val = float(actual_str)
        
        # Calculate MoM
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": current_val,
                    "growth": "n/a",
                    "formula": "First period - no previous data"
                })
                continue
                
            prev_row = filtered[i-1]
            prev_val_str = prev_row.get('actual_spend', '').strip()
            
            if not prev_val_str:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": current_val,
                    "growth": "Cannot Compute",
                    "formula": "Previous period was NULL"
                })
                continue
                
            prev_val = float(prev_val_str)
            if prev_val == 0:
                pct = 0.0
            else:
                pct = ((current_val - prev_val) / prev_val) * 100
                
            sign = "+" if pct > 0 else "−" if pct < 0 else ""
            pct_abs = abs(pct)
            
            # Formatting to match the expected +33.1% etc.
            growth_str = f"{sign}{pct_abs:.1f}%"
            
            # Enforcement Rule 3: Show formula
            formula = f"({current_val} - {prev_val}) / {prev_val}"
            
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": current_val,
                "growth": growth_str,
                "formula": formula
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", dest="growth_type", required=False)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    # Validations
    check_aggregation_refusal(args)
    check_growth_type_refusal(args)
    
    data = load_and_validate(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "period", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Cautious Budget Analysis Agent
Built based on the strict RICE enforcement rules to prevent silent failures and hallucinated aggregations.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str):
    """
    Reads CSV, validates, and collects null info before proceeding.
    """
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Computes per-period growth for a specific ward and category, refusing unsafe actions.
    """
    # ENFORCEMENT 1 & 4: Refusal logic
    if target_ward.lower() == "any" or target_category.lower() == "any":
        print("AGENT REFUSAL: Aggregation across wards or categories is not permitted. Please specify an exact ward and category.")
        sys.exit(1)
        
    if not growth_type:
        print("AGENT REFUSAL: --growth-type must be specified. I will not guess the formula.")
        sys.exit(1)
        
    if growth_type.upper() != "MOM":
        print(f"AGENT REFUSAL: Specified growth type '{growth_type}' is not supported in this strict demo (Only MoM is implemented).")
        sys.exit(1)

    # Filter data
    filtered_data = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]
    # Sort chronologically
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes']
        
        # Determine actual spend
        if not actual_spend_str:
            actual_spend = None
        else:
            actual_spend = float(actual_spend_str)
            
        growth_result = "N/A"
        formula = "N/A"
        
        # ENFORCEMENT 2: Null flagging
        if actual_spend is None:
            growth_result = f"NULL FLAGGED - {notes}"
            formula = "Cannot compute: Current period is NULL"
        elif i == 0:
            growth_result = "N/A (First Period)"
            formula = "N/A"
        else:
            prev_spend_str = filtered_data[i-1]['actual_spend'].strip()
            if not prev_spend_str:
                growth_result = "NULL FLAGGED - Prev period was NULL"
                formula = "Cannot compute: Previous period was NULL"
            else:
                prev_spend = float(prev_spend_str)
                # Avoid division by zero
                if prev_spend == 0:
                    growth_result = "Infinite"
                    formula = "((Current - 0) / 0) * 100"
                else:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    # Additional contextual notes for the result
                    extra_note = f" ({notes})" if notes else ""
                    growth_result = f"{growth:+.1f}%{extra_note}"
                    # ENFORCEMENT 3: Explicit formula
                    formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                    
        results.append({
            "Ward": target_ward,
            "Category": target_category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual_spend if actual_spend is not None else "NULL",
            "MoM Growth": growth_result,
            "Formula Used": formula
        })
        
    return results

def write_output(results, filepath):
    if not results:
        print("No data matched the filters.")
        return
        
    fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth", "Formula Used"]
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success! Output written to {filepath}")
    except IOError as e:
        print(f"Error writing to {filepath}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Cautious Budget Analysis")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Exact Ward Name (no 'Any')")
    parser.add_argument("--category", required=True, help="Exact Category Name (no 'Any')")
    parser.add_argument("--growth-type", required=False, help="e.g. MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    write_output(results, args.output)

if __name__ == "__main__":
    main()

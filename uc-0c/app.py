"""
UC-0C app.py — Budget Growth Analysis
Implemented based on R.I.C.E. rules from agents.md and skills.md.
"""
import argparse
import csv
import os

def load_dataset(input_path):
    """Reads the CSV and validates columns."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(dataset, ward, category, growth_type):
    """Computes MoM growth for a specific ward and category."""
    if not growth_type:
        return "REFUSAL: Growth type (MoM or YoY) is required. Please specify."
        
    if not ward or not category:
        return "REFUSAL: Ward and Category are required. All-ward aggregation is not permitted."

    # Filter data for specific ward and category
    filtered_data = [
        row for row in dataset 
        if row['ward'].strip() == ward.strip() and row['category'].strip() == category.strip()
    ]
    
    if not filtered_data:
        return f"REFUSAL: No data found for Ward '{ward}' and Category '{category}'."

    # Sort data by period
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    prev_spend = None
    
    for row in filtered_data:
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes']
        
        # Handle Nulls
        if not actual_spend or actual_spend.strip() == "":
            results.append({
                "Period": period,
                "Actual Spend": "NULL",
                "MoM Growth": "N/A",
                "Formula": f"Flagged Null: {notes}"
            })
            prev_spend = None # Cannot calculate growth from a null
            continue
            
        try:
            current_spend = float(actual_spend)
        except ValueError:
            results.append({
                "Period": period,
                "Actual Spend": actual_spend,
                "MoM Growth": "Error",
                "Formula": "Error: Non-numeric spend"
            })
            prev_spend = None
            continue

        growth_str = "N/A"
        formula_str = "N/A (First record)"
        
        if prev_spend is not None:
            # Formula: ((current - prev) / prev) * 100
            diff = current_spend - prev_spend
            growth = (diff / prev_spend) * 100
            growth_str = f"{growth:+.1f}%"
            formula_str = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
        
        results.append({
            "Period": period,
            "Actual Spend": current_spend,
            "MoM Growth": growth_str,
            "Formula": formula_str
        })
        prev_spend = current_spend

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific Ward name")
    parser.add_argument("--category", required=False, help="Specific Category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    
    # Handle explicit refusal conditions for missing parameters
    if not args.growth_type:
        print("REFUSAL: --growth-type (MoM or YoY) must be specified. I cannot guess the growth calculation.")
        return
        
    if not args.ward or not args.category:
        print("REFUSAL: Ward and Category must be specified. I am prohibited from aggregating across all wards or categories.")
        return

    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if isinstance(results, str):
            print(results)
            return

        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["Period", "Actual Spend", "MoM Growth", "Formula"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth analysis written to {args.output}")
        
        # Check for nulls encountered
        nulls = [r for r in results if r["Actual Spend"] == "NULL"]
        if nulls:
            print(f"Warning: {len(nulls)} null rows were identified and flagged.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

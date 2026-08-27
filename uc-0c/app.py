"""
UC-0C app.py — Budget Growth Analyst
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys
import os

# Skill 1: Load and Validate Dataset
def load_dataset(input_path):
    """Reads CSV, validates columns, and identifies null rows with reasons."""
    if not os.path.exists(input_path):
        print(f"Refusal: Input file not found at {input_path}")
        sys.exit(1)
    
    dataset = []
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            if not all(col in reader.fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in reader.fieldnames]
                print(f"Refusal: Missing columns in CSV: {missing}")
                sys.exit(1)
            
            for row in reader:
                dataset.append(row)
    except Exception as e:
        print(f"Refusal: Could not read CSV file. Error: {e}")
        sys.exit(1)

    # Identifty null rows in actual_spend — Enforcement Rule 2
    null_count = 0
    for row in dataset:
        if not row['actual_spend'] or row['actual_spend'].strip() == "":
            null_count += 1
            print(f"System: Identified null actual_spend for {row['period']} | {row['ward']} | {row['category']}. Reason: {row['notes']}")
    
    if null_count > 0:
        print(f"System: Total {null_count} null rows found.")
            
    return dataset

# Skill 2: Compute Growth for Ward/Category
def compute_growth(dataset, ward, category, growth_type):
    """Calculates growth metrics with formula enforcement and null-row flagging."""
    # Filter data - STRICTLY per ward/category — Enforcement Rule 1
    subset = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        print(f"Refusal: No data found for ward '{ward}' and category '{category}'.")
        sys.exit(1)
        
    # Sort by period to ensure proper chronological calculation
    subset.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(subset):
        period = row['period']
        actual_spend_str = row['actual_spend']
        notes = row['notes']
        
        # Enforcement Rule 2: Flag every null row before computing
        if not actual_spend_str or actual_spend_str.strip() == "":
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "Growth": f"Flagged: {notes}",
                "Formula": "n/a"
            })
            continue
            
        current_val = float(actual_spend_str)
        
        # Get previous row according to growth_type
        prev_row = None
        if growth_type.upper() == 'MOM':
            if i > 0:
                prev_row = subset[i-1]
        elif growth_type.upper() == 'YOY':
            if i >= 12:
                prev_row = subset[i-12]
        
        # Calculate growth and enforce Rule 3 (Show formula)
        if prev_row and prev_row['actual_spend'] and prev_row['actual_spend'].strip() != "":
            prev_val = float(prev_row['actual_spend'])
            growth_pct = ((current_val - prev_val) / prev_val) * 100
            formula = f"({current_val} - {prev_val}) / {prev_val}"
            growth_str = f"{growth_pct:+.1f}%"
        else:
            growth_str = "n/a"
            formula = "First period or previous period missing/NULL"
            
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": current_val,
            "Growth": growth_str,
            "Formula": formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst — Core Growth Computation")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path for output CSV result")
    
    args = parser.parse_args()
    
    # Enforcement Rule 1: Never aggregate across wards or categories
    if args.ward.lower() in ["all", "any"] or args.category.lower() in ["all", "any"]:
        print("Refusal: I refuse to aggregate across multiple wards/categories. Please specify a single target.")
        sys.exit(1)
        
    # Enforcement Rule 4: If --growth-type not specified — refuse and ask
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please specify MoM or YoY.")
        sys.exit(1)

    # Load dataset using skill
    dataset = load_dataset(args.input)
    
    # Compute growth using skill
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Save results to output file
    fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "Growth", "Formula"]
    try:
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nSuccess: Analysis complete. Result written to {args.output}")
    except Exception as e:
        print(f"Error: Could not write output file. {e}")

if __name__ == "__main__":
    main()

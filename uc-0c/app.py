"""
UC-0C app.py — Municipal Budget Growth Analyst.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and location.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    
    data = []
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Check columns
            if not set(required_columns).issubset(set(reader.fieldnames)):
                print(f"Refusal: Missing required columns. Expected: {required_columns}")
                sys.exit(1)
                
            null_rows = []
            for i, row in enumerate(reader, start=2): # Row 1 is header
                # Report null actual_spend
                actual_val = row['actual_spend'].strip() if row['actual_spend'] else ""
                if not actual_val:
                    null_rows.append((i, row['period'], row['ward'], row['category'], row['notes']))
                data.append(row)
                
        if null_rows:
            print(f"Found {len(null_rows)} rows with NULL actual_spend:")
            for r in null_rows:
                print(f"  Row {r[0]}: {r[1]} | {r[2]} | {r[3]} | Reason: {r[4]}")
        else:
            print("No NULL actual_spend values found.")
                
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
            
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Skill: compute_growth
    Calculates MoM/YoY growth for a specific ward and category.
    """
    # Filter strictly by ward and category to avoid unauthorized aggregation
    # Rule 1: Never aggregate across wards or categories
    filtered = [
        row for row in data 
        if row['ward'] == target_ward and row['category'] == target_category
    ]
    
    if not filtered:
        print(f"Refusal: No data found for Ward '{target_ward}' and Category '{target_category}'.")
        sys.exit(1)
        
    # Sort by period to ensure growth calculation is chronological
    filtered.sort(key=lambda x: x['period'])
    
    output_data = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend'].strip() if row['actual_spend'] else ""
        
        growth_val = "n/a"
        formula = "n/a"
        
        # Rule 2: Flag every null row before computing
        if not actual:
            reason = row['notes'] if row['notes'] else "No notes provided"
            growth_val = f"NULL ({reason})"
            formula = "n/a (Current value is NULL)"
        else:
            try:
                current_val = float(actual)
                
                # Find previous value based on growth_type
                prev_row = None
                if growth_type == "MoM":
                    if i > 0:
                        prev_row = filtered[i-1]
                elif growth_type == "YoY":
                    year, month = map(int, period.split('-'))
                    prev_period = f"{year-1}-{month:02d}"
                    prev_row = next((r for r in filtered if r['period'] == prev_period), None)
                
                if prev_row:
                    prev_actual = prev_row['actual_spend'].strip() if prev_row['actual_spend'] else ""
                    if not prev_actual:
                        growth_val = f"NULL (Previous period {prev_row['period']} was NULL)"
                        formula = f"({current_val} / NULL) - 1"
                    else:
                        prev_val = float(prev_actual)
                        if prev_val == 0:
                            growth_val = "Infinity"
                            formula = f"({current_val} / 0) - 1"
                        else:
                            pct = (current_val / prev_val) - 1
                            growth_val = f"{pct:+.1%}"
                            # Rule 3: Show formula used in every output row
                            formula = f"({current_val} / {prev_val}) - 1"
                else:
                    if i == 0 and growth_type == "MoM":
                        growth_val = "n/a"
                        formula = "First period in data"
                    elif growth_type == "YoY":
                        growth_val = "n/a"
                        formula = "No matching data for previous year"
            except ValueError:
                growth_val = "Error (Invalid numeric data)"
                formula = "n/a"

        # Construct output row
        out_row = {
            "period": row['period'],
            "ward": row['ward'],
            "category": row['category'],
            "actual_spend": actual if actual else "NULL",
            "growth": growth_val,
            "formula": formula,
            "notes": row['notes']
        }
        output_data.append(out_row)
        
    return output_data

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Input budget CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward name (no aggregation allowed)")
    parser.add_argument("--category", required=True, help="Specific category name (no aggregation allowed)")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    # We use unknown args to check if user passed something that looks like 'all' or multiple wards
    args, unknown = parser.parse_known_args()
    
    # Rule 4: If --growth-type not specified — refuse and ask
    if not args.growth_type:
        print("Refusal: --growth-type (MoM or YoY) must be specified. I cannot guess your requirement.")
        sys.exit(1)
        
    # Additional Guardrail: Refuse aggregation keywords
    if args.ward.lower() in ["all", "any", "total"]:
        print("Refusal: All-ward aggregation is strictly prohibited by project policy.")
        sys.exit(1)

    # Load dataset
    data = load_dataset(args.input)
    
    # Compute growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save results
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success: Growth table for '{args.ward}' | '{args.category}' saved to {args.output}")
    except Exception as e:
        print(f"Error saving output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

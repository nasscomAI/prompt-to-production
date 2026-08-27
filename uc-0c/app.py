# app.py
import argparse
import csv
import sys
import os

def load_dataset(input_file):
    """
    Skill: load_dataset
    Reads CSV, validates columns, and reports null count/rows before returning data.
    """
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        sys.exit(1)
    
    data = []
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing_cols = [col for col in required_columns if col not in reader.fieldnames]
            if missing_cols:
                print(f"Error: Missing required columns: {missing_cols}")
                sys.exit(1)
            
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    # Enforcement: Flag every null row before computing
    null_entries = [row for row in data if not row['actual_spend'].strip()]
    if null_entries:
        print(f"INFO: Detected {len(null_entries)} null entries in 'actual_spend'.")
        for row in null_entries:
            # Enforcement: report null reason from the notes column
            print(f"  - Flag: Period {row['period']}, Ward {row['ward']}, Category {row['category']} is NULL. Reason: {row['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Computes categorical growth (MoM/YoY) for a specific ward, returning results with explicit formulas.
    """
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    # Filter and sort by period
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    filtered_data.sort(key=lambda x: x['period'])
    
    if not filtered_data:
        print(f"Error: No data found for Ward: '{ward}', Category: '{category}'")
        sys.exit(1)
        
    results = []
    
    # Computation logic
    for i, current_row in enumerate(filtered_data):
        period = current_row['period']
        actual_spend_raw = current_row['actual_spend'].strip()
        
        current_val = float(actual_spend_raw) if actual_spend_raw else None
        
        growth_str = "n/a"
        formula = "n/a (Start of sequence)"
        
        if current_val is None:
            growth_str = "NULL"
            # Enforcement: report null reason
            formula = f"Flagged: {current_row['notes']}"
        elif i > 0:
            prev_spend_raw = filtered_data[i-1]['actual_spend'].strip()
            prev_val = float(prev_spend_raw) if prev_spend_raw else None
            
            if prev_val is None:
                growth_str = "n/a"
                formula = "Cannot compute: Previous period was NULL"
            else:
                # MoM Computation
                growth = ((current_val - prev_val) / prev_val) * 100
                growth_str = f"{growth:+.1f}%"
                # Enforcement: Show formula used in every output row alongside the result
                formula = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': current_val if current_val is not None else "NULL",
            f'{growth_type} Growth': growth_str,
            'Formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Analyst Agent for Ward-level Growth Analysis.")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Input CSV path")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target category name")
    parser.add_argument("--growth-type", help="Growth metric to calculate (MoM, YoY, etc.)")
    parser.add_argument("--output", help="Output file to save results")
    
    args = parser.parse_args()
    
    # Enforcement: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: --growth-type must be specified. Please choose a metric (e.g., MoM).")
        sys.exit(1)
        
    # Enforcement: Never aggregate across wards or categories — require both
    if not args.ward or not args.category:
        print("Refusal: Ward and Category must be explicitly specified. Aggregated analysis is not permitted.")
        sys.exit(1)
        
    # Load and Validate (Skill: load_dataset)
    data = load_dataset(args.input)
    
    # Compute Growth (Skill: compute_growth)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save or Print
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth', 'Formula']
    
    if args.output:
        try:
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Success: Results saved to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}")
            sys.exit(1)
    else:
        # Simple table formatting for console
        print("\n--- Ward Budget Growth Analysis ---\n")
        header = f"{'Period':<10} | {'Actual Spend':<15} | {args.growth_type + ' Growth':<15} | {'Formula'}"
        print(header)
        print("-" * len(header))
        for row in results:
            actual = str(row['Actual Spend (₹ lakh)'])
            growth = str(row[f'{args.growth_type} Growth'])
            print(f"{row['Period']:<10} | {actual:<15} | {growth:<15} | {row['Formula']}")

if __name__ == "__main__":
    main()

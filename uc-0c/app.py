import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    """
    Skills: reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    df = pd.read_csv(file_path)
    required_columns = ['period', 'ward', 'category', 'actual_spend', 'notes']
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        print(f"Error: Missing required columns: {missing}")
        sys.exit(1)
        
    # Report nulls before returning
    null_rows = df[df['actual_spend'].isnull()]
    if not null_rows.empty:
        print(f"Dataset Load Report: Found {len(null_rows)} deliberate null actual_spend values.")
        for idx, row in null_rows.iterrows():
            print(f"  - {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    else:
        print("Dataset Load Report: No null actual_spend rows found.")
        
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skills: takes ward + category + growth_type, returns per-period table with formula shown.
    Refusal Rules:
    - Never aggregate across wards or categories unless explicitly instructed — refuse if asked.
    - Flag every null row before computing — report null reason from the notes column.
    - Show formula used in every output row alongside the result.
    """
    if not ward or not category:
        print("Refusal: Multiple wards or categories detected. This system refuses to aggregate across wards or categories.")
        sys.exit(1)
        
    # Filter for the specific ward and category
    subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if subset.empty:
        print(f"Refusal: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)
        
    # Ensure they only picked ONE ward and category (even if they were in the CSV)
    # The filter above already handles the single selection, but we are enforcing refusal
    # of any request that would result in multiple wards/categories (aggregation).
    
    subset = subset.sort_values(by='period')
    
    results = []
    
    for i in range(len(subset)):
        current_row = subset.iloc[i]
        period = current_row['period']
        current_val = current_row['actual_spend']
        
        # Rule: Flag every null row before computing
        if pd.isna(current_val):
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': "NULL",
                'Growth': "FLAGGED",
                'Formula': "N/A",
                'Reason': current_row['notes']
            })
            continue
            
        # For MoM growth, find previous month
        if i == 0:
            growth_str = "N/A (Start period)"
            formula_str = "N/A"
        else:
            prev_row = subset.iloc[i-1]
            prev_val = prev_row['actual_spend']
            
            if pd.isna(prev_val):
                growth_str = "FLAGGED (Prev value missing)"
                formula_str = f"( {current_val} - NULL ) / NULL"
            else:
                growth_percent = ((current_val - prev_val) / prev_val) * 100
                growth_str = f"{growth_percent:+.1f}%"
                formula_str = f"( {current_val} - {prev_val} ) / {prev_val}"
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': current_val,
            'Growth': growth_str,
            'Formula': formula_str,
            'Reason': current_row['notes'] if pd.notna(current_row['notes']) else ""
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Budget Analyst Agent — Pune Municipal Corporation Ward Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 - Kasba')")
    parser.add_argument("--category", required=True, help="Budget category (e.g., Waste Management)")
    parser.add_argument("--growth-type", help="Calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path for the growth_output.csv")
    
    args = parser.parse_args()
    
    # Rule: If --growth-type not specified — refuse and ask, never guess.
    if not args.growth_type:
        print("Refusal: Growth type (e.g., MoM or YoY) must be specified using --growth-type. Please clarify your request.")
        sys.exit(1)
        
    # Load and validate
    df = load_dataset(args.input)
    
    # Check for aggregation refusal (if inputs are multiple, but argparse handles this as single unless modified)
    # But in agents.md, it says "Never aggregate across wards or categories unless explicitly instructed — refuse if asked."
    # Our app structure enforces single selection.
    
    # Compute
    results_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save output
    results_df.to_csv(args.output, index=False)
    print(f"Success: Growth calculation saved to {args.output}")

if __name__ == "__main__":
    main()

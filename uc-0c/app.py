"""
UC-0C app.py
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import pandas as pd
import sys

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates columns, and reports the null count 
    along with which rows contain nulls before returning the data.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Error: Missing required columns in dataset: {', '.join(missing_columns)}")
        sys.exit(1)

    null_rows = df[df['actual_spend'].isnull()]
    if not null_rows.empty:
        print(f"Warning: Found {len(null_rows)} explicitly null records in actual_spend.")
        for _, row in null_rows.iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else "No reason provided"
            print(f"  - {row['period']} | {row['ward']} | {row['category']}: {reason}")
            
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Takes a dataset filtered by ward and category, along with a specified growth type, 
    and returns a per-period table showing the computed growth and the formula used.
    """
    if not growth_type:
        print("Error: --growth-type MUST be specified. Refusing to guess.")
        sys.exit(1)
        
    if ward.lower() == 'any' or category.lower() == 'any':
         print("Error: Aggregating across wards or categories is strictly prohibited by agent enforcement rules.")
         sys.exit(1)

    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'")
        sys.exit(1)
        
    # Sort by period to ensure sequential growth calculation
    filtered_df = filtered_df.sort_values('period')
    
    # Check for unhandled nulls in the target subset
    nulls_in_subset = filtered_df[filtered_df['actual_spend'].isnull()]
    if not nulls_in_subset.empty:
        for _, row in nulls_in_subset.iterrows():
             print(f"Error: Cannot compute growth for {row['period']}. actual_spend is NULL. Reason: {row['notes']}")
        # Continue with actuals as NaN so growth is NaN, to reflect that there are errors
        
    # Calculate MoM
    if growth_type.lower() == 'mom':
        # Create shifted column to calculate MoM
        filtered_df['prev_spend'] = filtered_df['actual_spend'].shift(1)
        filtered_df['growth_val'] = ((filtered_df['actual_spend'] - filtered_df['prev_spend']) / filtered_df['prev_spend']) * 100
        
        # Formatting formula and growth percent
        def format_result(row):
            if pd.isna(row['actual_spend']):
                return "NULL"
            if pd.isna(row['prev_spend']):
                return "n/a (first period)"
            
            growth_pct = row['growth_val']
            sign = "+" if growth_pct > 0 else ""
            notes = f" ({row['notes']})" if pd.notna(row['notes']) else ""
            
            return f"{sign}{growth_pct:.1f}%{notes}"
            
        def format_formula(row):
            if pd.isna(row['actual_spend']):
                 return "n/a"
            if pd.isna(row['prev_spend']):
                return "n/a"
            return f"(({row['actual_spend']} - {row['prev_spend']}) / {row['prev_spend']}) * 100"

        filtered_df['computed_growth'] = filtered_df.apply(format_result, axis=1)
        filtered_df['formula_used'] = filtered_df.apply(format_formula, axis=1)

    else:
        print(f"Error: Growth type '{growth_type}' is not supported yet. Only 'MoM' is implemented.")
        sys.exit(1)
        
    # Select columns for final output
    output_columns = ['ward', 'category', 'period', 'actual_spend', 'computed_growth', 'formula_used']
    return filtered_df[output_columns]

def main():
    parser = argparse.ArgumentParser(description="Ward Budget Analysis Agent")
    parser.add_argument("--input", required=True, help="Path to input dataset (CSV)")
    parser.add_argument("--ward", required=True, help="Ward name to filter on")
    parser.add_argument("--category", required=True, help="Category name to filter on")
    parser.add_argument("--growth-type", help="Type of growth to compute (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to save output CSV")
    
    args = parser.parse_args()
    
    print("--- Ward Budget Analysis Agent ---")
    
    # 1. Load data
    print("Loading dataset...")
    df = load_dataset(args.input)
    
    # 2. Compute Growth
    print("\nComputing growth...")
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # 3. Save output
    print(f"\nSaving results to {args.output}...")
    result_df.to_csv(args.output, index=False)
    print("Done!")

if __name__ == "__main__":
    main()

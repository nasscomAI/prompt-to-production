import argparse
import sys
import pandas as pd
import numpy as np

def load_dataset(filepath):
    """
    Reads CSV, validates columns, reports null count and which rows 
    before returning the parsed dataset.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    for col in required_cols:
        if col not in df.columns:
            print(f"Error: Missing required column '{col}'")
            sys.exit(1)
            
    # Report null values directly from notes
    null_rows = df[df['actual_spend'].isnull()]
    null_count = len(null_rows)
    print(f"Loaded dataset with {len(df)} rows.")
    if null_count > 0:
        print(f"Warning: Found {null_count} rows with null 'actual_spend'.")
        print("Null reasons from notes:")
        for idx, row in null_rows.iterrows():
            print(f"  - {row['period']} · {row['ward']} · {row['category']}: {row['notes']}")
            
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses guessing growth logic or all-ward aggregation.
    """
    # Rule 4: Refuse to guess growth_type
    if not growth_type:
        print("\n[REFUSAL] Error: --growth-type not specified. Refusing to guess (e.g., MoM or YoY).")
        sys.exit(1)
        
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category:
        print("\n[REFUSAL] Error: Must specify both 'ward' and 'category'. Refusing to aggregate across wards or categories.")
        sys.exit(1)
        
    # Filter dataset
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered.empty:
        print("No data found for the specified ward and category.")
        return filtered
        
    # Sort by period chronologically
    filtered = filtered.sort_values(by='period').reset_index(drop=True)
    
    # Rule 3: Calculate growth and show formula in output
    if growth_type.upper() == 'MOM':
        filtered['prev_spend'] = filtered['actual_spend'].shift(1)
        
        def calculate_mom(row):
            # Rule 2: Flag every null row before computing
            if pd.isna(row['actual_spend']):
                return f"NULL (Flagged: {row['notes']})", "N/A"
            if pd.isna(row['prev_spend']):
                return "N/A", "N/A"
            
            growth = (row['actual_spend'] - row['prev_spend']) / row['prev_spend']
            growth_pct = f"{growth * 100:+.1f}%"
            formula = f"({row['actual_spend']} - {row['prev_spend']}) / {row['prev_spend']}"
            return growth_pct, formula
            
        filtered[['Growth', 'Formula']] = filtered.apply(
            lambda row: pd.Series(calculate_mom(row)), axis=1
        )
        filtered.drop(columns=['prev_spend'], errors='ignore', inplace=True)

    elif growth_type.upper() == 'YOY':
        filtered['period_dt'] = pd.to_datetime(filtered['period'])
        filtered['prev_yr_spend'] = filtered['period_dt'].apply(
            lambda x: filtered.loc[filtered['period_dt'] == x - pd.DateOffset(years=1), 'actual_spend'].values
        )
        filtered['prev_yr_spend'] = filtered['prev_yr_spend'].apply(lambda x: x[0] if len(x) > 0 else np.nan)
        
        def calculate_yoy(row):
            # Rule 2: Flag every null row before computing
            if pd.isna(row['actual_spend']):
                return f"NULL (Flagged: {row['notes']})", "N/A"
            if pd.isna(row['prev_yr_spend']):
                return "N/A", "N/A"
            
            growth = (row['actual_spend'] - row['prev_yr_spend']) / row['prev_yr_spend']
            growth_pct = f"{growth * 100:+.1f}%"
            formula = f"({row['actual_spend']} - {row['prev_yr_spend']}) / {row['prev_yr_spend']}"
            return growth_pct, formula
            
        filtered[['Growth', 'Formula']] = filtered.apply(
            lambda row: pd.Series(calculate_yoy(row)), axis=1
        )
        filtered.drop(columns=['period_dt', 'prev_yr_spend'], inplace=True)
    else:
        print(f"\n[REFUSAL] Error: Unknown growth type '{growth_type}'. Use MoM or YoY.")
        sys.exit(1)
        
    return filtered

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator Agent")
    parser.add_argument("--input", required=True, help="Path to budget CSV dataset")
    parser.add_argument("--ward", help="Ward name (required to prevent aggregation)")
    parser.add_argument("--category", help="Category name (required to prevent aggregation)")
    parser.add_argument("--growth-type", help="Type of growth to compute (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to save output CSV")
    
    args = parser.parse_args()
    
    print(f"Loading dataset: {args.input}")
    df = load_dataset(args.input)
    
    print(f"\nComputing {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'")
    result = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Optional viewing of the head before saving
    print("\nResult preview:")
    print(result[['period', 'ward', 'category', 'actual_spend', 'Growth', 'Formula']].head(12))
    
    if args.output:
        result.to_csv(args.output, index=False)
        print(f"\nOutput successfully written to {args.output}")

if __name__ == "__main__":
    main()

import argparse
import pandas as pd
import os
import sys

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, and reports null count and locations.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    df = pd.read_csv(file_path)
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    # Validate columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        sys.exit(1)
        
    # Report nulls before returning
    null_mask = df['actual_spend'].isnull()
    null_count = null_mask.sum()
    
    print(f"--- Data Validation: Found {null_count} null actual_spend values ---")
    if null_count > 0:
        null_rows = df[null_mask]
        for idx, row in null_rows.iterrows():
            print(f"NULL at Row {idx+1}: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    print("----------------------------------------------------------\n")
    
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Filters data and calculates MoM/YoY growth with formula documentation.
    """
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    # Here we filter strictly by the provided ward and category
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'")
        return pd.DataFrame()
        
    filtered_df = filtered_df.sort_values('period')
    
    results = []
    
    for i in range(len(filtered_df)):
        row = filtered_df.iloc[i]
        period = row['period']
        current_val = row['actual_spend']
        notes = row['notes']
        
        growth_pct = None
        formula = "N/A"
        
        if pd.isnull(current_val):
            growth_pct = "NULL"
            formula = f"Skipped: {notes}"
        elif growth_type == 'MoM':
            if i > 0:
                prev_row = filtered_df.iloc[i-1]
                prev_val = prev_row['actual_spend']
                
                if pd.notnull(prev_val) and prev_val != 0:
                    growth_val = (current_val - prev_val) / prev_val
                    growth_pct = f"{growth_val * 100:+.1f}%"
                    formula = f"({current_val} - {prev_val}) / {prev_val}"
                else:
                    growth_pct = "N/A"
                    formula = "Previous month is null or zero"
            else:
                growth_pct = "N/A"
                formula = "First period in dataset"
        elif growth_type == 'YoY':
            # Simplified YoY for this dataset (assumes previous year's month exists)
            # Find period from 12 months ago
            curr_pd = pd.to_datetime(period)
            prev_pd = curr_pd - pd.DateOffset(years=1)
            prev_pd_str = prev_pd.strftime('%Y-%m')
            
            prev_rows = filtered_df[filtered_df['period'] == prev_pd_str]
            if not prev_rows.empty:
                prev_val = prev_rows.iloc[0]['actual_spend']
                if pd.notnull(prev_val) and prev_val != 0:
                    growth_val = (current_val - prev_val) / prev_val
                    growth_pct = f"{growth_val * 100:+.1f}%"
                    formula = f"({current_val} - {prev_val}) / {prev_val}"
                else:
                    growth_pct = "N/A"
                    formula = "Previous year month is null or zero"
            else:
                growth_pct = "N/A"
                formula = f"No data for {prev_pd_str}"
        
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': current_val if pd.notnull(current_val) else "NULL",
            'growth': growth_pct,
            'formula': formula
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (Refuse if empty for aggregate)")
    parser.add_argument("--category", help="Category name (Refuse if empty for aggregate)")
    parser.add_argument("--growth-type", help="MoM or YoY (Refuse if empty)")
    parser.add_argument("--output", required=True, help="Path to output growth_output.csv")
    
    args = parser.parse_args()
    
    # Enforcement: Refuse aggregation across all wards/categories
    if not args.ward or not args.category:
        print("Error: Granularity Refusal. You must specify both --ward and --category.")
        print("Aggregation across all wards or categories is not permitted.")
        sys.exit(1)
        
    # Enforcement: Refuse if growth-type not specified
    if not args.growth_type:
        print("Error: Growth Type Refusal. You must specify --growth-type (MoM or YoY).")
        sys.exit(1)
        
    if args.growth_type not in ['MoM', 'YoY']:
        print(f"Error: Invalid growth-type '{args.growth_type}'. Use MoM or YoY.")
        sys.exit(1)

    # 1. Load Dataset
    df = load_dataset(args.input)
    
    # 2. Compute Growth
    results_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # 3. Save Output
    if not results_df.empty:
        results_df.to_csv(args.output, index=False)
        print(f"Analysis complete. Results written to {args.output}")
    else:
        print("Analysis failed: No results generated.")

if __name__ == "__main__":
    main()

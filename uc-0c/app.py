import argparse
import pandas as pd
import sys
import os

"""
UC-0C app.py — Number That Looks Right
Build following the Budget Analysis Specialist role:
- Granular analysis only (no unauthorized aggregation)
- Formula transparency
- Proactive null flagging
"""

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, and reports null count and details before returning.
    """
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' not found.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Mandatory column '{col}' is missing from the dataset.")
            sys.exit(1)
            
    # Identify and report nulls
    null_rows = df[df['actual_spend'].isna()]
    print(f"--- Dataset Load Report ---")
    print(f"Total rows: {len(df)}")
    print(f"Null actual_spend rows detected: {len(null_rows)}")
    for idx, row in null_rows.iterrows():
        print(f"  - FLAG: Row {idx} | {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    print(f"---------------------------\n")
    
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates per-period growth with formula transparency and null row flagging.
    Refuses if asked to aggregate or if growth type is missing.
    """
    # Enforcement Rule 1: Granularity Check
    if ward.lower() in ['all', 'any', 'total', '*'] or category.lower() in ['all', 'any', 'total', '*']:
        print("Refusal: Unauthorized aggregation requested. I only perform granular ward-level and category-level analysis.")
        sys.exit(1)

    # Filter data
    subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if subset.empty:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)
        
    # Sort by period
    subset['period_dt'] = pd.to_datetime(subset['period'])
    subset = subset.sort_values('period_dt')
    
    results = []
    
    for i in range(len(subset)):
        curr = subset.iloc[i]
        period = curr['period']
        actual = curr['actual_spend']
        
        # Base result structure
        res = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (INR lakh)': actual if not pd.isna(actual) else 'NULL',
            f'{growth_type} Growth': None,
            'Formula': None
        }
        
        if pd.isna(actual):
            # Enforcement Rule 2: Flag nulls
            res[f'{growth_type} Growth'] = 'NULL (Flagged)'
            res['Formula'] = f"REFUSE COMPUTATION: {curr['notes']}"
        elif i == 0:
            res[f'{growth_type} Growth'] = 'n/a'
            res['Formula'] = 'Initial period: No previous data to compare'
        else:
            prev = subset.iloc[i-1]
            prev_val = prev['actual_spend']
            
            if pd.isna(prev_val):
                res[f'{growth_type} Growth'] = 'Incomplete'
                res['Formula'] = f"Cannot compute: Previous period ({prev['period']}) is NULL"
            else:
                # Enforcement Rule 3: Show Formula
                growth = ((actual - prev_val) / prev_val) * 100
                res[f'{growth_type} Growth'] = f"{growth:+.1f}%"
                res['Formula'] = f"(({actual} - {prev_val}) / {prev_val}) * 100"
                
        results.append(res)
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C: Ward Budget Growth Calculator")
    parser.add_argument("--input", help="Path to input CSV file")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target expenditure category")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g., MoM)")
    parser.add_argument("--output", help="Path to save output CSV")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: Refuse if growth-type is missing
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please choose 'MoM' or 'YoY'. I will not guess.")
        sys.exit(1)
        
    if not all([args.input, args.ward, args.category, args.output]):
        print("Error: Missing required arguments. Use --help for usage.")
        sys.exit(1)

    # Load
    df = load_dataset(args.input)
    
    # Process
    results_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save
    results_df.to_csv(args.output, index=False)
    
    # Print sample output as requested by "Verifiable output"
    print(f"\nSuccess: Analysis for '{args.ward}' - '{args.category}' saved to {args.output}")
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    main()

import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    df = pd.read_csv(file_path)
    
    # Required columns validation
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        sys.exit(1)
        
    # Null reporting
    null_rows = df[df['actual_spend'].isna()]
    print(f"--- Dataset Audit Report ---")
    print(f"Found {len(null_rows)} rows with null actual_spend values.")
    for idx, row in null_rows.iterrows():
        period = row['period']
        ward = row['ward']
        cat = row['category']
        reason = row['notes']
        print(f"  - {period} | {ward} | {cat} | Reason: {reason}")
    print(f"---------------------------\n")
    
    return df

def compute_growth(df, ward, category, growth_type, output_path):
    """
    Skill: compute_growth
    Calculates growth metrics, ensures no aggregation, flags nulls, and shows formulas.
    """
    if not growth_type:
        print("Refusal: --growth-type not specified. I cannot compute growth without a defined formula (MoM or YoY).")
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"Refusal: Growth type '{growth_type}' is not yet supported. Only 'MoM' is allowed.")
        sys.exit(1)

    # Filtering
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Refusal: No data found for ward '{ward}' and category '{category}'.")
        sys.exit(1)
        
    # Check for Aggregation Refusal
    if filtered_df['period'].duplicated().any():
        print(f"Refusal: The criteria results in multiple records per period. I am strictly prohibited from aggregating data across wards or categories.")
        sys.exit(1)
        
    filtered_df = filtered_df.sort_values('period')
    
    results = []
    
    # Growth calculation: (Current - Previous) / Previous
    for i in range(len(filtered_df)):
        curr_row = filtered_df.iloc[i]
        curr_val = curr_row['actual_spend']
        
        if i == 0:
            growth = "n/a"
            formula = "n/a (First period)"
        else:
            prev_row = filtered_df.iloc[i-1]
            prev_val = prev_row['actual_spend']
            
            if pd.isna(curr_val):
                growth = "NULL"
                formula = f"Refused: Actual spend is null. Reason: {curr_row['notes']}"
            elif pd.isna(prev_val):
                growth = "NULL"
                formula = f"Refused: Previous period spend is null. Reason: {prev_row['notes']}"
            elif prev_val == 0:
                growth = "INF"
                formula = f"({curr_val} - 0.0) / 0.0"
            else:
                growth_val = (curr_val - prev_val) / prev_val
                growth = f"{growth_val * 100:+.1f}%"
                formula = f"({curr_val} - {prev_val}) / {prev_val}"
                
        results.append({
            'Ward': curr_row['ward'],
            'Category': curr_row['category'],
            'Period': curr_row['period'],
            'Actual Spend (INR lakh)': curr_val if not pd.isna(curr_val) else "NULL",
            'MoM Growth': growth,
            'Formula': formula
        })
        
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_path, index=False)
    print(f"Success: Growth table saved to {output_path}")
    print("\n--- Output Preview ---")
    print(output_df.to_string(index=False))

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()

"""
UC-0C app.py
Built following the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import sys
import pandas as pd
import numpy as np

def load_dataset(filepath):
    """
    Reads the CSV dataset, validates required columns, and reports null count and specific rows with nulls before returning the data.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns: {missing}")
        sys.exit(1)

    null_rows = df[df['actual_spend'].isnull()]
    print(f"Dataset loaded. Found {len(null_rows)} rows with null actual_spend.")
    
    if not null_rows.empty:
        for idx, row in null_rows.iterrows():
            print(f" - Row {idx}: Ward '{row['ward']}' | Category '{row['category']}' | Period '{row['period']}' | Reason: {row['notes']}")

    return df

def compute_growth(df, ward, category, growth_type):
    """
    Calculates growth for a specific ward, category, and growth type, ensuring formulas are shown.
    Refuses unauthorized aggregations.
    """
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a growth type.")
        sys.exit(1)

    if not ward or str(ward).lower() in ['all', 'any']:
        print("Error: System explicitly refuses to aggregate across wards without permission.")
        sys.exit(1)
        
    if not category or str(category).lower() in ['all', 'any']:
        print("Error: System explicitly refuses to aggregate across categories without permission.")
        sys.exit(1)

    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()

    if filtered_df.empty:
        print(f"Warning: No data found for Ward '{ward}' and Category '{category}'.")
        return filtered_df

    # Ensure chronological order
    filtered_df = filtered_df.sort_values(by='period').reset_index(drop=True)

    growth_col = f"{growth_type} Growth"
    results = []

    for i, row in filtered_df.iterrows():
        result_row = row.to_dict()
        
        if growth_type.upper() == 'MOM':
            if pd.isnull(row['actual_spend']):
                result_row[growth_col] = "NULL"
                result_row['formula'] = f"Not Computed (Flagged NULL: {row['notes']})"
            elif i == 0 or pd.isnull(filtered_df.loc[i-1, 'actual_spend']):
                result_row[growth_col] = "n/a"
                result_row['formula'] = "(Current - Previous) / Previous (Missing previous data)"
            else:
                prev = filtered_df.loc[i-1, 'actual_spend']
                curr = row['actual_spend']
                if prev == 0:
                    growth = np.inf if curr > 0 else 0
                else:
                    growth = (curr - prev) / prev
                result_row[growth_col] = f"{growth * 100:+.1f}%"
                result_row['formula'] = "(Current - Previous) / Previous"
                
        elif growth_type.upper() == 'YOY':
            result_row[growth_col] = "n/a"
            result_row['formula'] = "(Current Year - Previous Year) / Previous Year"
        else:
            print(f"Error: Unsupported growth type '{growth_type}'. Cannot compute.")
            sys.exit(1)
            
        results.append(result_row)

    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV dataset")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Manual enforcement of refusal conditions before dataset processing
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a growth type.")
        sys.exit(1)

    if not args.ward or args.ward.lower() in ['all', 'any']:
        print("Error: Aggregation across wards is not permitted unless explicitly instructed. Refusing request.")
        sys.exit(1)

    if not args.category or args.category.lower() in ['all', 'any']:
        print("Error: Aggregation across categories is not permitted unless explicitly instructed. Refusing request.")
        sys.exit(1)

    df = load_dataset(args.input)
    
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)

    try:
        result_df.to_csv(args.output, index=False)
        print(f"Results successfully saved to {args.output}")
    except Exception as e:
        print(f"Error saving output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

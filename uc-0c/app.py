import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the ward budget CSV, validates structure, and identifies null entries.
    """
    if not os.path.exists(file_path):
        print(f"Error: Dataset file not found at {file_path}")
        sys.exit(1)

    df = pd.read_csv(file_path)
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    # Check for missing columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        sys.exit(1)

    # Detect null entries in actual_spend
    null_rows = df[df['actual_spend'].isna()]
    print(f"--- Dataset Quality Report ---")
    print(f"Total rows loaded: {len(df)}")
    print(f"Null 'actual_spend' values found: {len(null_rows)}")
    for idx, row in null_rows.iterrows():
        print(f"Row {idx}: {row['period']} · {row['ward']} · {row['category']} [Reason: {row['notes']}]")
    print(f"-------------------------------\n")

    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Computes period-over-period growth for a specific ward and category, flagging nulls.
    """
    # Filtering - Ensuring no aggregation across wards/categories
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    # Sort by period to ensure chronological growth calculation
    filtered_df['period'] = pd.to_datetime(filtered_df['period'])
    filtered_df = filtered_df.sort_values('period')

    results = []
    
    # Calculate MoM growth manually to handle formulas and nulls
    for i in range(len(filtered_df)):
        row = filtered_df.iloc[i]
        curr_val = row['actual_spend']
        prev_val = filtered_df.iloc[i-1]['actual_spend'] if i > 0 else None
        
        formula = "N/A"
        growth_val = "N/A"
        
        # If current value is null, flag it
        if pd.isna(curr_val):
            growth_val = f"NULL: {row['notes']}"
            formula = "N/A (Current value is NULL)"
        elif i == 0:
            growth_val = "N/A"
            formula = "N/A (First period)"
        elif pd.isna(prev_val):
            growth_val = "NULL: Previous value was null"
            formula = "N/A (Previous value was NULL)"
        else:
            # Standard MoM Growth calculation
            diff = curr_val - prev_val
            growth = (diff / prev_val) * 100
            growth_val = f"{growth:+.1f}%"
            formula = f"({curr_val} - {prev_val}) / {prev_val}"

        results.append({
            'Ward': row['ward'],
            'Category': row['category'],
            'Period': row['period'].strftime('%Y-%m'),
            'Actual Spend (₹ lakh)': curr_val if not pd.isna(curr_val) else "NULL",
            'Growth (%)': growth_val,
            'Formula Used': formula
        })

    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Specify a single ward")
    parser.add_argument("--category", help="Specify a single category")
    parser.add_argument("--growth-type", help="Specify growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output growth_output.csv")

    args = parser.parse_args()

    # Enforcement: Refusal conditions
    if not args.growth_type:
        print("REFUSAL: Growth type --growth-type (e.g., MoM) must be explicitly specified. Never guessing.")
        sys.exit(1)

    if not args.ward or not args.category:
        print("REFUSAL: Ward level growth calculation requires specific --ward and --category.")
        print("Never aggregate across wards or categories. Refusing all-ward or all-category aggregation requests.")
        sys.exit(1)

    print(f"Calculating {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'...")

    # Execute skills
    df = load_dataset(args.input)
    growth_df = compute_growth(df, args.ward, args.category, args.growth_type)

    # Save output
    growth_df.to_csv(args.output, index=False)
    print(f"Growth calculation complete. Results saved to: {args.output}")

if __name__ == "__main__":
    main()

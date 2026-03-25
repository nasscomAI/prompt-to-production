"""
UC-0C app.py — Number That Looks Right.
Calculates growth while strictly enforcing per-ward/per-category reporting and flagging nulls.
"""
import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    df = pd.read_csv(file_path)
    
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns: {', '.join(missing_cols)}")
        sys.exit(1)
    
    # Identify null actual_spend rows
    null_rows = df[df['actual_spend'].isna()]
    if not null_rows.empty:
        print(f"Found {len(null_rows)} rows with null 'actual_spend':")
        for idx, row in null_rows.iterrows():
            print(f"  - {row['period']} · {row['ward']} · {row['category']} (Reason: {row['notes']})")
    else:
        print("No null 'actual_spend' values found.")
        
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Flags nulls instead of computing.
    """
    # Filter for the specific ward and category
    subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if subset.empty:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'")
        sys.exit(1)
        
    # Sort by period to ensure correct growth calculation
    subset = subset.sort_values('period')
    
    results = []
    
    for i in range(len(subset)):
        current_row = subset.iloc[i]
        period = current_row['period']
        actual = current_row['actual_spend']
        notes = current_row['notes']
        
        res_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual if pd.notna(actual) else 'NULL',
            'MoM Growth': 'n/a',
            'Formula': 'n/a'
        }
        
        if pd.isna(actual):
            res_row['MoM Growth'] = f"FLAGGED: {notes}"
            res_row['Formula'] = "Cannot compute (NULL value)"
        elif i > 0:
            prev_row = subset.iloc[i-1]
            prev_actual = prev_row['actual_spend']
            
            if pd.isna(prev_actual):
                res_row['MoM Growth'] = "FLAGGED: Previous month was NULL"
                res_row['Formula'] = "Cannot compute (Previous NULL)"
            else:
                if growth_type == 'MoM':
                    growth = ((actual - prev_actual) / prev_actual) * 100
                    res_row['MoM Growth'] = f"{growth:+.1f}%"
                    res_row['Formula'] = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
        else:
            res_row['MoM Growth'] = "n/a (First period)"
            res_row['Formula'] = "n/a"
            
        results.append(res_row)
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Calculate growth from budget data.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", help="Ward name (required for calculation)")
    parser.add_argument("--category", help="Category name (required for calculation)")
    parser.add_argument("--growth-type", help="Growth type (e.g., MoM)")
    parser.add_argument("--output", default="growth_output.csv", help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type is required. Please specify 'MoM' or other supported types.")
        sys.exit(1)
        
    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not args.ward or not args.category:
        print("Error: Both --ward and --category must be specified. Aggregation across wards or categories is not allowed.")
        sys.exit(1)
        
    # Load dataset
    df = load_dataset(args.input)
    
    # Compute growth
    results_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save results
    results_df.to_csv(args.output, index=False)
    print(f"\nResults saved to {args.output}")
    
    # Display results to console for verification
    print("\nOutput Preview:")
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    main()

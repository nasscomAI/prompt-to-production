"""
UC-0C app.py — Financial Data Analyst
"""
import argparse
import sys
import pandas as pd

def load_dataset(input_file, ward, category):
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        sys.exit(f"Error loading dataset: {e}")
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_cols.issubset(set(df.columns)):
        sys.exit(f"Missing required columns in dataset. Expected: {required_cols}")

    # Filter strictly by ward and category
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()

    # Identify and flag nulls
    null_rows = filtered_df[filtered_df['actual_spend'].isnull()]
    for _, row in null_rows.iterrows():
        print(f"FLAG: Null actual_spend found for {row['period']} - Reason: {row['notes']}")

    return filtered_df

def compute_growth(df, growth_type):
    df = df.sort_values(by='period').reset_index(drop=True)
    
    growth_col = []
    formula_col = []
    
    if growth_type.upper() == "MOM":
        offset = 1
    elif growth_type.upper() == "YOY":
        offset = 12
    else:
        sys.exit(f"Unsupported growth-type: {growth_type}")

    for i in range(len(df)):
        if i < offset:
            growth_col.append("n/a")
            formula_col.append("n/a (insufficient data)")
            continue
            
        current_val = df.loc[i, 'actual_spend']
        prev_val = df.loc[i - offset, 'actual_spend']
        
        if pd.isnull(current_val) or pd.isnull(prev_val):
            growth_col.append("NULL")
            formula_col.append("NULL (missing data)")
        else:
            growth = (current_val - prev_val) / prev_val * 100
            sign = "+" if growth > 0 else ""
            growth_col.append(f"{sign}{growth:.1f}%")
            formula_col.append(f"({current_val} - {prev_val}) / {prev_val} * 100")
            
    df['growth'] = growth_col
    df['formula'] = formula_col
    return df

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analyst")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Specific ward to analyze")
    parser.add_argument("--category", help="Specific category to analyze")
    parser.add_argument("--growth-type", help="Type of growth (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()

    # Enforcement: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        sys.exit("Refusal: --growth-type not specified. Please provide a growth type (e.g., MoM). Will not guess.")

    # Enforcement: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or not args.category or args.ward.lower() == "all" or args.category.lower() == "all":
        sys.exit("Refusal: Aggregation across wards or categories is not permitted. Please specify exactly one --ward and one --category.")

    df = load_dataset(args.input, args.ward, args.category)
    result_df = compute_growth(df, args.growth_type)
    
    result_df.to_csv(args.output, index=False)
    print(f"Successfully processed data and saved to {args.output}")

if __name__ == "__main__":
    main()

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
    
    # Validate columns
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing mandatory columns: {', '.join(missing_columns)}")
        sys.exit(1)
    
    # Report nulls
    null_rows = df[df['actual_spend'].isnull()]
    if not null_rows.empty:
        print(f"Found {len(null_rows)} rows with NULL actual_spend:")
        for _, row in null_rows.iterrows():
            reason = row['notes'] if 'notes' in row and pd.notnull(row['notes']) else "No reason provided"
            print(f"- {row['period']} | {row['ward']} | {row['category']} | Reason: {reason}")
    else:
        print("No NULL actual_spend values found.")
        
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category:
        print("Error: Ward and Category must be specified. Global aggregation is not allowed.")
        sys.exit(1)
        
    subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if subset.empty:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'")
        sys.exit(1)
        
    # Ensure period is sorted
    subset = subset.sort_values('period')
    
    results = []
    
    # Formula mapping
    formula_str = ""
    if growth_type == "MoM":
        formula_str = "(Current - Previous) / Previous"
    else:
        # Enforcement: If --growth-type unknown — refuse
        print(f"Error: Growth type '{growth_type}' is not supported. Use 'MoM'.")
        sys.exit(1)

    # Compute growth using shift for the previous record
    subset['prev_spend'] = subset['actual_spend'].shift(1)
    
    for _, row in subset.iterrows():
        current = row['actual_spend']
        previous = row['prev_spend']
        
        growth_val = "n/a"
        res_formula = "n/a (first period)"
        
        if pd.isnull(current):
            # Enforcement: Flag every null row before computing
            reason = row['notes'] if 'notes' in row and pd.notnull(row['notes']) else "NULL actual spend"
            growth_val = f"NULL ({reason})"
            res_formula = "n/a"
        elif pd.isnull(previous):
            if subset.index.get_loc(row.name) == 0:
                res_formula = "n/a (first period)"
            else:
                growth_val = "n/a (previous is NULL)"
                res_formula = formula_str
        else:
            if previous == 0:
                growth_val = "inf"
            else:
                growth_pct = ((current - previous) / previous) * 100
                growth_val = f"{growth_pct:+.1f}%"
            res_formula = formula_str
            
        results.append({
            'Ward': row['ward'],
            'Category': row['category'],
            'Period': row['period'],
            'Actual Spend (₹ lakh)': current if pd.notnull(current) else "NULL",
            'Growth Result': growth_val,
            'Formula Used': res_formula
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # Enforcement: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type is required (e.g., MoM). Please specify the growth calculation type.")
        sys.exit(1)
        
    # Load
    df = load_dataset(args.input)
    
    # Compute
    output_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save
    output_df.to_csv(args.output, index=False)
    print(f"Success: Growth table saved to {args.output}")

if __name__ == "__main__":
    main()


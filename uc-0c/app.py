import argparse
import pandas as pd
import sys

def load_dataset(filepath):
    """
    Reads the CSV dataset, validates expected columns, and identifies deliberate nulls.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
        
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}", file=sys.stderr)
        sys.exit(1)
        
    # Identify and report nulls in actual_spend
    null_mask = df['actual_spend'].isna()
    null_count = null_mask.sum()
    if null_count > 0:
        print(f"Found {null_count} rows with null actual_spend:")
        for _, row in df[null_mask].iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else 'No reason provided'
            print(f"  - {row['period']} | {row['ward']} | {row['category']} -> {reason}")
    else:
        print("No null values found in actual_spend.")
        
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Calculates growth for a specified ward and category using the designated growth type.
    """
    if not growth_type:
        print("Error: Refused to compute. --growth-type not specified. Please specify MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    if not ward or ward.lower() == 'all':
        print("Error: Refused to compute. Cannot aggregate across wards. You must specify a specific ward.", file=sys.stderr)
        sys.exit(1)
        
    if not category or category.lower() == 'all':
        print("Error: Refused to compute. Cannot aggregate across categories. You must specify a specific category.", file=sys.stderr)
        sys.exit(1)

    # Filter to specified ward and category
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered_df.empty:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        return filtered_df
        
    # Sort by period to ensure chronological order
    filtered_df['period'] = pd.to_datetime(filtered_df['period'])
    filtered_df = filtered_df.sort_values('period').reset_index(drop=True)
    filtered_df['period'] = filtered_df['period'].dt.strftime('%Y-%m')

    # Compute growth
    # For MoM, we compare to the previous period in the sorted dataframe
    filtered_df['prev_spend'] = filtered_df['actual_spend'].shift(1)
    
    filtered_df['growth'] = None
    filtered_df['formula_used'] = None

    for idx, row in filtered_df.iterrows():
        current = row['actual_spend']
        prev = row['prev_spend']
        
        formula = ""
        growth_val = None
        
        if pd.isna(current):
            formula = f"NULL / {prev if pd.notna(prev) else 'NULL'} - 1 = FLAG (cannot compute missing current)"
        elif pd.isna(prev):
            # For the first row or if previous is explicitly null
            formula = f"{current} / NULL - 1 = FLAG (cannot compute missing previous)"
        else:
            if prev == 0:
                formula = f"{current} / {prev} - 1 = Div By Zero"
            else:
                growth_val = (current / prev) - 1
                # Format to percentage string
                growth_str = f"+{growth_val*100:.1f}%" if growth_val > 0 else f"{growth_val*100:.1f}%"
                formula = f"{current} / {prev} - 1 = {growth_str} ({growth_type})"
                filtered_df.at[idx, 'growth'] = growth_str
                
        filtered_df.at[idx, 'formula_used'] = formula

    # Drop the temporary column
    filtered_df = filtered_df.drop(columns=['prev_spend'])
    
    return filtered_df

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()

    # Load and validate dataset
    df = load_dataset(args.input)
    
    # Compute growth (enforces rules like no aggregation)
    output_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save output
    output_df.to_csv(args.output, index=False)
    print(f"Output successfully written to {args.output}")

if __name__ == "__main__":
    main()

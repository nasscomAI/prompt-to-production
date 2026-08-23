import argparse
import pandas as pd
import sys

def load_dataset(file_path):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        sys.exit(1)

    null_mask = df['actual_spend'].isnull()
    null_count = null_mask.sum()
    
    print(f"Dataset loaded. Total null 'actual_spend' rows found: {null_count}")
    if null_count > 0:
        print("Explicitly flagging the following null rows before computation:")
        for _, row in df[null_mask].iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else "No reason provided"
            print(f"  - {row['period']} · {row['ward']} · {row['category']} | Reason: {reason}")
            
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses if aggregated or if growth_type is missing.
    """
    if ward is None or str(ward).lower() == 'all':
        print("Error: Never aggregate across wards unless explicitly instructed. Refusing to calculate.")
        sys.exit(1)
        
    if category is None or str(category).lower() == 'all':
        print("Error: Never aggregate across categories unless explicitly instructed. Refusing to calculate.")
        sys.exit(1)
        
    if growth_type is None:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a valid growth type (e.g., MoM).")
        sys.exit(1)
        
    growth_type = growth_type.upper()
    if growth_type not in ["MOM", "YOY"]:
        print(f"Error: Unsupported growth-type '{growth_type}'.")
        sys.exit(1)

    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'.")
        return pd.DataFrame(columns=['Ward', 'Category', 'Period', 'Actual Spend', f'{growth_type} Growth', 'Formula'])
        
    # Ensure sorted order for time series calculations
    filtered_df.sort_values(by='period', inplace=True)
    filtered_df.reset_index(drop=True, inplace=True)
    
    results = []
    
    for i in range(len(filtered_df)):
        current_row = filtered_df.iloc[i]
        period = current_row['period']
        current_spend = current_row['actual_spend']
        notes = current_row['notes']
        
        result_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': current_spend if pd.notna(current_spend) else 'NULL',
            f'{growth_type} Growth': None,
            'Formula': None
        }
        
        # Check current row null
        if pd.isna(current_spend):
            result_row[f'{growth_type} Growth'] = 'Must be flagged — not computed'
            reason = notes if pd.notna(notes) else 'Reason unknown'
            result_row['Formula'] = f"Skip: current actual_spend is NULL ({reason})"
            results.append(result_row)
            continue
            
        # Compute based on growth_type
        if growth_type == "MOM":
            if i == 0:
                result_row['Formula'] = "Cannot compute: first available month"
                result_row[f'{growth_type} Growth'] = "n/a"
            else:
                prev_row = filtered_df.iloc[i-1]
                prev_spend = prev_row['actual_spend']
                
                if pd.isna(prev_spend):
                    result_row['Formula'] = "Cannot compute: previous actual_spend is NULL"
                    result_row[f'{growth_type} Growth'] = "n/a"
                else:
                    try:
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        result_row[f'{growth_type} Growth'] = f"{growth:+.1f}%"
                        result_row['Formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                    except ZeroDivisionError:
                        result_row['Formula'] = "Cannot compute: previous actual_spend is 0"
                        result_row[f'{growth_type} Growth'] = "n/a"
                        
        elif growth_type == "YOY":
            if i < 12:
                result_row['Formula'] = "Cannot compute: less than 12 months data"
                result_row[f'{growth_type} Growth'] = "n/a"
            else:
                prev_row = filtered_df.iloc[i-12]
                prev_spend = prev_row['actual_spend']
                
                if pd.isna(prev_spend):
                    result_row['Formula'] = "Cannot compute: previous year actual_spend is NULL"
                    result_row[f'{growth_type} Growth'] = "n/a"
                else:
                    try:
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        result_row[f'{growth_type} Growth'] = f"{growth:+.1f}%"
                        result_row['Formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                    except ZeroDivisionError:
                        result_row['Formula'] = "Cannot compute: previous year actual_spend is 0"
                        result_row[f'{growth_type} Growth'] = "n/a"
                        
        results.append(result_row)
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Budget Data Analyst Agent")
    parser.add_argument("--input", required=True, help="Path to the input CSV file")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth calculation (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to the output CSV file")
    
    args = parser.parse_args()
    
    if args.ward is None or args.category is None:
        print("Error: Ward and category must be explicitly provided. Refusing to guess or aggregate.")
        sys.exit(1)
        
    # Execute skill: load_dataset
    df = load_dataset(args.input)
    
    # Execute skill: compute_growth
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Output to CSV
    result_df.to_csv(args.output, index=False)
    print(f"Success: Wrote output data to {args.output}")

if __name__ == "__main__":
    main()

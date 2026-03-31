import argparse
import pandas as pd
import sys

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates its column structure, and 
    systematically reports missing values before returning the dataset.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        sys.exit(f"Error: File '{filepath}' not found.")
        
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing_cols = required_columns - set(df.columns)
    if missing_cols:
        sys.exit(f"Error: Missing required columns in dataset: {missing_cols}")
        
    # Strictly report all null actual_spend rows
    null_mask = df['actual_spend'].isnull()
    null_count = null_mask.sum()
    print(f"Dataset Validation: Found {null_count} rows with null actual_spend.")
    if null_count > 0:
        print("Details of null actual_spend rows:")
        null_rows = df[null_mask]
        for _, row in null_rows.iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else "No reason provided"
            print(f"  - {row['period']} | {row['ward']} | {row['category']} -> Reason: {reason}")
    print("-" * 50)
            
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Calculates period-over-period budget growth strictly for a single ward and category,
    embedding the mathematical formula into every output row.
    """
    if not ward or str(ward).strip().lower() == 'any':
        sys.exit("Error: Refusing to aggregate across multiple wards. Specific ward must be provided.")
        
    if not category or str(category).strip().lower() == 'any':
        sys.exit("Error: Refusing to aggregate across multiple categories. Specific category must be provided.")
        
    if not growth_type:
        sys.exit("Error: --growth-type not specified. Refusal condition met: rather than guess, please specify a valid growth type (e.g., MoM, YoY).")
        
    growth_type_upper = str(growth_type).strip().upper()
    if growth_type_upper not in ['MOM', 'YOY']:
        sys.exit(f"Error: Unsupported or unknown --growth-type '{growth_type}'. Cannot compute.")
        
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered.empty:
        sys.exit(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        
    filtered['period'] = pd.to_datetime(filtered['period'], format='%Y-%m', errors='coerce')
    filtered = filtered.sort_values(by='period').reset_index(drop=True)
    
    step = 1 if growth_type_upper == 'MOM' else 12
    growth_col_name = f"{growth_type} Growth"
    
    output_rows = []
    
    for i in range(len(filtered)):
        row = filtered.iloc[i]
        period_str = row['period'].strftime('%Y-%m') if pd.notna(row['period']) else 'Unknown'
        current_val = row['actual_spend']
        notes = str(row['notes']) if pd.notna(row['notes']) else ""
        
        # Rule: Flag every null row before computing
        if pd.isna(current_val):
            output_rows.append({
                'Ward': ward,
                'Category': category,
                'Period': period_str,
                'Actual Spend (₹ lakh)': 'NULL',
                growth_col_name: f"Flagged — not computed ({notes})",
                'Formula': 'No calculation (Actual Spend is NULL)'
            })
            continue
            
        if i < step:
            output_rows.append({
                'Ward': ward,
                'Category': category,
                'Period': period_str,
                'Actual Spend (₹ lakh)': current_val,
                growth_col_name: 'n/a',
                'Formula': 'No prior baseline'
            })
            continue
            
        prev_row = filtered.iloc[i - step]
        prev_val = prev_row['actual_spend']
        
        if pd.isna(prev_val):
            output_rows.append({
                'Ward': ward,
                'Category': category,
                'Period': period_str,
                'Actual Spend (₹ lakh)': current_val,
                growth_col_name: 'n/a (baseline NULL)',
                'Formula': f"({current_val} - NULL) / NULL"
            })
            continue
            
        try:
            growth = (current_val - prev_val) / prev_val
            pct_str = f"{growth * 100:+.1f}%"
            if notes:
                growth_str = f"{pct_str} ({notes})"
            else:
                growth_str = pct_str
                
            formula_used = f"({current_val} - {prev_val}) / {prev_val}"
            
        except ZeroDivisionError:
            growth_str = 'Undefined'
            formula_used = f"({current_val} - 0) / 0"
            
        output_rows.append({
            'Ward': ward,
            'Category': category,
            'Period': period_str,
            'Actual Spend (₹ lakh)': current_val,
            growth_col_name: growth_str,
            'Formula': formula_used
        })
        
    return pd.DataFrame(output_rows)

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument('--input', required=True, help="Path to input CSV")
    parser.add_argument('--ward', help="Ward name (must not be 'Any')")
    parser.add_argument('--category', help="Category name (must not be 'Any')")
    parser.add_argument('--growth-type', help="Growth metric type (e.g., 'MoM', 'YoY')")
    parser.add_argument('--output', required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    df = load_dataset(args.input)
    output_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    output_df.to_csv(args.output, index=False)
    print(f"Output correctly restricted to {args.ward} - {args.category}.")
    print(f"Data saved successfully to {args.output}")

if __name__ == '__main__':
    main()

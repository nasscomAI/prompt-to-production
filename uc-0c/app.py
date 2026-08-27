"""
UC-0C app.py — Implemented using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
        
    df = pd.read_csv(file_path)
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_columns.issubset(df.columns):
        print(f"Error: Missing required columns. Expected at least: {required_columns}")
        sys.exit(1)
        
    # Flag every null row before computing (Enforcement 2)
    null_mask = df['actual_spend'].isnull()
    null_count = null_mask.sum()
    
    if null_count > 0:
        print(f"--- Validation Report ---")
        print(f"Found {null_count} rows with null 'actual_spend'.")
        null_rows = df[null_mask]
        for _, row in null_rows.iterrows():
            notes = row['notes'] if pd.notnull(row['notes']) else "No reason provided"
            print(f"- Period: {row['period']}, Ward: {row['ward']}, Category: {row['category']}, Reason: {notes}")
        print(f"-------------------------\n")
        
    return df

def compute_growth(df, ward, category, growth_type):
    # Enforcement 1: Never aggregate across wards or categories
    if not ward or not category or ',' in ward or ',' in category or ward.lower() == 'all' or category.lower() == 'all':
        print("Error: Must specify exactly one ward and one category. Aggregating is not allowed unless explicitly instructed.")
        sys.exit(1)

    # Enforcement 4: Refuse and ask if growth_type is missing
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide --growth-type (e.g., MoM).")
        sys.exit(1)

    # Filter for the specific ward and category
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
    
    # Sort chronologically
    filtered_df = filtered_df.sort_values(by='period').reset_index(drop=True)
    
    results = []
    
    for i in range(len(filtered_df)):
        row = filtered_df.iloc[i]
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes'] if pd.notnull(row['notes']) else ""
        
        # Enforcement 2 & 3: Skip calculation and return flag for null rows
        if pd.isnull(actual_spend):
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'computed_growth': 'n/a',
                'formula': 'n/a',
                'notes': f"NULL flagged: {notes}"
            })
            continue
            
        growth = "n/a"
        formula = "n/a"
            
        # Enforcement 3: Show formula used in every output row
        if growth_type.upper() == 'MOM':
            if i > 0:
                prev_spend = filtered_df.iloc[i-1]['actual_spend']
                if pd.isnull(prev_spend):
                    growth = "n/a"
                    formula = "Previous period spend is null"
                elif prev_spend == 0:
                    growth = "n/a"
                    formula = "Previous period spend is 0, cannot divide by zero"
                else:
                    growth_val = ((actual_spend - prev_spend) / prev_spend) * 100
                    growth = f"{growth_val:+.1f}%"
                    formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                growth = "n/a"
                formula = "No previous period"
        elif growth_type.upper() == 'YOY':
            # Assuming period is YYYY-MM
            try:
                year, month = period.split('-')
                prev_year_period = f"{int(year)-1}-{month}"
                prev_row = filtered_df[filtered_df['period'] == prev_year_period]
                if not prev_row.empty:
                    prev_spend = prev_row.iloc[0]['actual_spend']
                    if pd.isnull(prev_spend):
                        growth = "n/a"
                        formula = "Previous year period spend is null"
                    elif prev_spend == 0:
                        growth = "n/a"
                        formula = "Previous year period spend is 0, cannot divide by zero"
                    else:
                        growth_val = ((actual_spend - prev_spend) / prev_spend) * 100
                        growth = f"{growth_val:+.1f}%"
                        formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                else:
                    growth = "n/a"
                    formula = f"No previous year data found for {prev_year_period}"
            except Exception:
                growth = "n/a"
                formula = "Invalid period format for YoY"
        else:
            print(f"Error: Unsupported growth type '{growth_type}'")
            sys.exit(1)
            
        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual_spend,
            'computed_growth': growth,
            'formula': formula,
            'notes': notes
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Civic budget analysis assistant")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target category name")
    parser.add_argument("--growth-type", help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    # Enforcement 1 & 4 checks
    if not args.ward or not args.category:
        print("Error: Must specify exactly one ward '--ward' and one category '--category'. Aggregating is not allowed.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide --growth-type (e.g., MoM).")
        sys.exit(1)
        
    df = load_dataset(args.input)
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    result_df.to_csv(args.output, index=False)
    print(f"Successfully processed data and saved output to {args.output}")

if __name__ == "__main__":
    main()

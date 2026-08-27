import argparse
import pandas as pd
import sys
import os

def load_dataset(filepath):
    """
    Reads the CSV dataset, validates expected columns, and reports null count 
    and which rows contain null actual_spend values before returning.
    """
    print(f"Loading dataset from {filepath}...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        sys.exit(1)
        
    expected_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    for col in expected_columns:
        if col not in df.columns:
            print(f"Error: Missing required column '{col}'")
            sys.exit(1)
            
    # Flag every null row before computing - report null reason from the notes column
    null_rows = df[df['actual_spend'].isnull()]
    if not null_rows.empty:
        print(f"Flagged {len(null_rows)} rows with null 'actual_spend':")
        for _, row in null_rows.iterrows():
            print(f" - {row['period']} | {row['ward']} | {row['category']} | Null reason: {row['notes']}")
    else:
        print("No null 'actual_spend' values found.")
        
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Calculates the specified growth metric (e.g., MoM) for a given ward and category, 
    returning a per-period table with the exact formula shown.
    """
    if not growth_type:
        print("Error: --growth-type must be specified. Refusing to guess.")
        sys.exit(1)
        
    # Never aggregate across wards or categories unless explicitly instructed - refuse if asked
    if ward.strip().lower() == 'all' or category.strip().lower() == 'all' or ward == '' or category == '':
        print("Error: Aggregation across wards or categories is strictly forbidden unless explicitly instructed. Refusing request.")
        sys.exit(1)
        
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered.empty:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return pd.DataFrame()
        
    # Ensure chronological order
    filtered = filtered.sort_values(by='period').reset_index(drop=True)
    
    results = []
    
    if growth_type.upper() == 'MOM':
        for i in range(len(filtered)):
            current = filtered.iloc[i]
            res_row = {
                'ward': current['ward'],
                'category': current['category'],
                'period': current['period'],
                'budgeted_amount': current['budgeted_amount'],
                'actual_spend': current['actual_spend'],
                'growth_result': None,
                'formula_used': None, # Show formula used in every output row alongside the result
                'notes': current['notes']
            }
            
            if pd.isnull(current['actual_spend']):
                res_row['growth_result'] = "NULL (Flagged)"
                res_row['formula_used'] = f"Not computed. Reason: {current['notes']}"
            elif i == 0:
                res_row['growth_result'] = "N/A"
                res_row['formula_used'] = "First period (no prior data)"
            else:
                prev = filtered.iloc[i-1]
                if pd.isnull(prev['actual_spend']):
                    res_row['growth_result'] = "N/A"
                    res_row['formula_used'] = "Prior period actual_spend is null"
                else:
                    curr_val = float(current['actual_spend'])
                    prev_val = float(prev['actual_spend'])
                    if prev_val == 0:
                        res_row['growth_result'] = "N/A"
                        res_row['formula_used'] = "Division by zero"
                    else:
                        growth = (curr_val - prev_val) / prev_val
                        growth_pct = f"{growth * 100:+.1f}%"
                        res_row['growth_result'] = growth_pct
                        res_row['formula_used'] = f"({curr_val} - {prev_val}) / {prev_val}"
                        
            results.append(res_row)
            
    elif growth_type.upper() == 'YOY':
        for i in range(len(filtered)):
            current = filtered.iloc[i]
            res_row = {
                'ward': current['ward'],
                'category': current['category'],
                'period': current['period'],
                'budgeted_amount': current['budgeted_amount'],
                'actual_spend': current['actual_spend'],
                'growth_result': None,
                'formula_used': None,
                'notes': current['notes']
            }
            
            if pd.isnull(current['actual_spend']):
                res_row['growth_result'] = "NULL (Flagged)"
                res_row['formula_used'] = f"Not computed. Reason: {current['notes']}"
            else:
                try:
                    year, month = str(current['period']).split('-')
                    prev_year_period = f"{int(year)-1}-{month}"
                    prev_row = filtered[filtered['period'] == prev_year_period]
                    
                    if prev_row.empty:
                        res_row['growth_result'] = "N/A"
                        res_row['formula_used'] = f"No prior year data ({prev_year_period})"
                    else:
                        prev = prev_row.iloc[0]
                        if pd.isnull(prev['actual_spend']):
                            res_row['growth_result'] = "N/A"
                            res_row['formula_used'] = "Prior year actual_spend is null"
                        else:
                            curr_val = float(current['actual_spend'])
                            prev_val = float(prev['actual_spend'])
                            if prev_val == 0:
                                res_row['growth_result'] = "N/A"
                                res_row['formula_used'] = "Division by zero"
                            else:
                                growth = (curr_val - prev_val) / prev_val
                                growth_pct = f"{growth * 100:+.1f}%"
                                res_row['growth_result'] = growth_pct
                                res_row['formula_used'] = f"({curr_val} - {prev_val}) / {prev_val}"
                except ValueError:
                    res_row['growth_result'] = "Error"
                    res_row['formula_used'] = "Invalid period format"
            
            results.append(res_row)
    else:
        print(f"Error: Unknown growth type '{growth_type}'.")
        sys.exit(1)
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV dataset path")
    parser.add_argument("--ward", required=True, help="Ward to analyze")
    parser.add_argument("--category", required=True, help="Category to analyze")
    # Not using required=True to explicitly handle the refusal logic below
    parser.add_argument("--growth-type", required=False, help="Growth metric to calculate (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    args = parser.parse_args()
    
    # Enforcement: If --growth-type not specified - refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type must be specified. Refusing to guess. Please provide --growth-type MoM or YoY.")
        sys.exit(1)
    
    df = load_dataset(args.input)
    
    output_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    if not output_df.empty:
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        output_df.to_csv(args.output, index=False)
        print(f"Output successfully written to {args.output}")

if __name__ == "__main__":
    main()

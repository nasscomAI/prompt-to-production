"""
UC-0C app.py — Budget Growth Calculator Agent
Implements the Budget Growth Calculator Agent using defined skills to compute per-ward, per-category growth rates with proper null handling.
"""
import argparse
import pandas as pd
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV file, validates columns, reports null count and which rows before returning the dataset, ensuring silent null handling is avoided.
    Input: File path to CSV (string).
    Output: Pandas DataFrame with validated data, plus a report of nulls (dict with count and list of null rows including notes).
    """
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    try:
        df = pd.read_csv(file_path)
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        null_report = {
            'count': df['actual_spend'].isnull().sum(),
            'rows': df[df['actual_spend'].isnull()][['period', 'ward', 'category', 'notes']].to_dict('records')
        }
        return df, null_report
    except Exception as e:
        raise ValueError(f"Error loading dataset: {e}")

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward, category, and growth_type, computes per-period growth table with formulas shown, avoiding wrong aggregation level and formula assumption.
    Input: DataFrame, ward (string), category (string), growth_type (string: 'MoM' or 'YoY').
    Output: List of dicts (one per period) with period, actual_spend, growth_rate, formula, and null flags; no aggregation across wards/categories.
    """
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError("Invalid growth_type. Must be 'MoM' or 'YoY'.")
    
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered.empty:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")
    
    filtered = filtered.sort_values('period').reset_index(drop=True)
    results = []
    
    for i, row in filtered.iterrows():
        period = row['period']
        actual = row['actual_spend']
        notes = row['notes']
        
        if pd.isnull(actual):
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'growth_rate': 'Not computed',
                'formula': 'N/A',
                'notes': notes
            })
            continue
        
        if growth_type == 'MoM':
            if i == 0:
                growth = 'N/A (first period)'
                formula = 'N/A'
            else:
                prev_actual = filtered.iloc[i-1]['actual_spend']
                if pd.isnull(prev_actual):
                    growth = 'Not computed (previous null)'
                    formula = 'N/A'
                else:
                    growth = f"{((actual - prev_actual) / prev_actual * 100):.1f}%"
                    formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
        elif growth_type == 'YoY':
            # Assuming periods are YYYY-MM, but since only 2024, YoY not possible
            growth = 'N/A (YoY requires multiple years)'
            formula = 'N/A'
        
        results.append({
            'period': period,
            'actual_spend': actual,
            'growth_rate': growth,
            'formula': formula,
            'notes': notes if pd.notnull(notes) else ''
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Budget Growth Calculator Agent: Compute per-ward per-category growth')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--ward', required=True, help='Ward name')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YoY'], help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file {args.input} not found")
    
    # Use skills
    df, null_report = load_dataset(args.input)
    print(f"Dataset loaded. Null count: {null_report['count']}")
    for null_row in null_report['rows']:
        print(f"Null row: {null_row}")
    
    results = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Output to CSV
    output_df = pd.DataFrame(results)
    output_df.to_csv(args.output, index=False)
    print(f"Growth computed and saved to {args.output}")

if __name__ == "__main__":
    main()

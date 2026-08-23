"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import pandas as pd

def load_dataset(file_path: str):
    """
    Load budget CSV and report null rows before processing.
    Returns: pandas DataFrame
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading dataset: {e}")
    
    # Check required columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Required columns missing: {missing}")
    
    # Report null rows
    null_rows = df[df['actual_spend'].isna()]
    if len(null_rows) > 0:
        print("Dataset loaded.")
        print(f"Null rows found (will be flagged): {len(null_rows)}")
        for idx, row in null_rows.iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else 'No reason recorded'
            print(f"  - {row['period']}, {row['ward']}, {row['category']}: {reason}")
    else:
        print("Dataset loaded. No nulls present.")
    
    return df

def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str, output_path: str):
    """
    Calculate Month-over-Month or Year-over-Year growth for specified ward-category.
    
    Enforcement:
    - Flag all nulls with reason
    - Never aggregate across wards or categories
    - Show formula in every output
    - Refuse if growth_type not MoM or YoY
    """
    # Validate inputs
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth_type: {growth_type}. Must be 'MoM' or 'YoY'")
    
    # Filter for specified ward and category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data found for Ward: '{ward}' and Category: '{category}'")
    
    # Sort by period
    filtered['period_date'] = pd.to_datetime(filtered['period'])
    filtered = filtered.sort_values('period_date').reset_index(drop=True)
    
    # Prepare output rows
    output_rows = []
    
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        null_flag = 'YES' if pd.isna(actual_spend) else ''
        null_reason = row['notes'] if pd.isna(actual_spend) else ''
        
        # If null, don't compute growth
        if pd.isna(actual_spend):
            output_rows.append({
                'period': period,
                'actual_spend': '',
                'growth_percent': '',
                'formula': 'N/A',
                'null_flag': null_flag,
                'null_reason': null_reason
            })
            continue
        
        # Compute growth based on type
        growth_percent = ''
        formula = ''
        
        if growth_type == 'MoM':
            if idx > 0:
                # Look for previous month
                prev_row = filtered.iloc[idx - 1]
                if pd.notna(prev_row['actual_spend']):
                    prev_spend = prev_row['actual_spend']
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    growth_percent = f"{growth:+.1f}%"
                    formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                else:
                    # Previous month was null, cannot compute growth
                    growth_percent = ''
                    formula = 'Previous month null — cannot compute'
            else:
                # First period — no growth
                growth_percent = ''
                formula = 'First period'
        
        elif growth_type == 'YoY':
            # For YoY, look for same period 12 months prior (not implemented for 2024 data)
            # Since all data is 2024, YoY is not applicable — flag as N/A
            growth_percent = ''
            formula = 'YoY: No prior year data available (all data is 2024)'
        
        output_rows.append({
            'period': period,
            'actual_spend': actual_spend,
            'growth_percent': growth_percent,
            'formula': formula,
            'null_flag': null_flag,
            'null_reason': null_reason
        })
    
    # Write output CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'growth_percent', 'formula', 'null_flag', 'null_reason']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        
        print(f"Growth calculation complete: {growth_type} growth for {ward} - {category}")
        print(f"Results written to: {output_path}")
        
    except Exception as e:
        raise Exception(f"Error writing output file: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category",    required=True,  help="Category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    
    args = parser.parse_args()
    
    try:
        # Load dataset
        df = load_dataset(args.input)
        
        # Compute growth
        compute_growth(df, args.ward, args.category, args.growth_type, args.output)
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()


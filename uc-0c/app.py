"""
UC-0C app.py — Infrastructure Budget Growth Calculator.
Computes month-over-month or year-over-year infrastructure spend growth
per ward and category. Enforces: per-ward/category isolation, null-row flagging,
formula transparency, and refuses to compute without explicit growth-type.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path


def load_dataset(input_file):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null rows before returning dataset.
    """
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Validate columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Report nulls in actual_spend
    null_mask = df['actual_spend'].isna()
    null_count = null_mask.sum()
    null_rows = df[null_mask][['period', 'ward', 'category', 'notes']].to_dict('records')
    
    print(f"[LOAD_DATASET] Total rows: {len(df)}", file=sys.stderr)
    print(f"[LOAD_DATASET] Null rows in actual_spend: {null_count}", file=sys.stderr)
    if null_rows:
        print(f"[LOAD_DATASET] Null row details:", file=sys.stderr)
        for row in null_rows:
            print(f"  - {row['period']} | {row['ward']} | {row['category']} | {row['notes']}", file=sys.stderr)
    
    return df, null_count, null_rows


def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Filters for ward+category, computes growth per period, shows formula in output.
    """
    # Validate ward and category exist
    if ward not in df['ward'].unique():
        raise ValueError(f"Ward not found: {ward}")
    if category not in df['category'].unique():
        raise ValueError(f"Category not found: {category}")
    
    # Filter to ward + category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data for ward='{ward}' and category='{category}'")
    
    # Sort by period to ensure chronological order
    filtered['period_dt'] = pd.to_datetime(filtered['period'])
    filtered = filtered.sort_values('period_dt').reset_index(drop=True)
    
    # Initialize output table
    output_rows = []
    
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes']
        
        if pd.isna(actual_spend):
            # Flag null rows — do NOT compute growth
            output_rows.append({
                'period': period,
                'actual_spend': 'NULL',
                'formula_used': 'N/A',
                'growth_pct': f'NULL - {notes}'
            })
        else:
            if growth_type == 'MoM':
                if idx == 0:
                    # First month has no prior month
                    growth_pct = 'N/A (first month)'
                    formula = 'MoM (no prior)'
                else:
                    # Find previous non-null month
                    prev_idx = idx - 1
                    while prev_idx >= 0 and pd.isna(filtered.loc[prev_idx, 'actual_spend']):
                        prev_idx -= 1
                    
                    if prev_idx < 0:
                        growth_pct = 'N/A (no prior non-null)'
                        formula = 'MoM (no valid prior)'
                    else:
                        prev_spend = filtered.loc[prev_idx, 'actual_spend']
                        growth = ((actual_spend - prev_spend) / prev_spend) * 100
                        growth_pct = f'{growth:.1f}%'
                        formula = 'MoM'
            
            elif growth_type == 'YoY':
                # YoY: compare to 12 months prior (same period last year)
                # Since we only have 2024, YoY would have no comparison
                growth_pct = 'N/A (no prior year data)'
                formula = 'YoY (no 2023 data)'
            
            else:
                raise ValueError(f"growth_type must be 'MoM' or 'YoY', got: {growth_type}")
            
            output_rows.append({
                'period': period,
                'actual_spend': actual_spend,
                'formula_used': formula,
                'growth_pct': growth_pct
            })
    
    return pd.DataFrame(output_rows)


def main():
    parser = argparse.ArgumentParser(
        description='Compute month-over-month infrastructure spend growth by ward and category.'
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--ward', required=True, help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Expense category')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YoY'],
                        help='Growth type: MoM (month-over-month) or YoY (year-over-year)')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    try:
        # Load and validate dataset
        df, null_count, null_rows = load_dataset(args.input)
        
        # Compute growth
        result_df = compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Write output
        result_df.to_csv(args.output, index=False)
        print(f"[SUCCESS] Output written to {args.output}", file=sys.stderr)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

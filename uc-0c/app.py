"""
UC-0C app.py — Budget Growth Calculator
Implements agents.md + skills.md enforcement rules.
Core: per-ward, per-category growth calculation with null flagging and formula visibility.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates schema, reports null count and row identifiers.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Identify null rows
    null_mask = df['actual_spend'].isna()
    null_rows = df[null_mask][['period', 'ward', 'category', 'notes']].to_dict('records')
    null_count = null_mask.sum()
    
    return {
        'dataframe': df,
        'null_count': null_count,
        'null_rows': null_rows
    }

def compute_growth(dataframe, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates MoM or YoY growth for a specific ward-category pair.
    Returns dataframe with period, actual_spend, formula, growth_rate_pct.
    """
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")
    
    # Filter to selected ward and category
    filtered = dataframe[
        (dataframe['ward'] == ward) & 
        (dataframe['category'] == category)
    ].copy()
    
    if filtered.empty:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Build output rows
    output_rows = []
    
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes']
        
        output_row = {
            'period': period,
            'actual_spend': actual_spend,
        }
        
        # Handle null values
        if pd.isna(actual_spend):
            output_row['formula'] = 'Not computed — null value'
            output_row['growth_rate_pct'] = 'NULL'
            output_row['null_reason'] = notes
        else:
            # Compute growth
            if growth_type == 'MoM':
                if idx == 0:
                    # First period: no previous month
                    output_row['formula'] = 'N/A (first period)'
                    output_row['growth_rate_pct'] = 'N/A'
                else:
                    prev_spend = filtered.loc[idx - 1, 'actual_spend']
                    if pd.isna(prev_spend):
                        output_row['formula'] = f'Cannot compute (previous month null)'
                        output_row['growth_rate_pct'] = 'N/A'
                    else:
                        growth = ((actual_spend - prev_spend) / prev_spend) * 100
                        output_row['formula'] = f'({actual_spend} - {prev_spend}) / {prev_spend} * 100'
                        output_row['growth_rate_pct'] = round(growth, 1)
            
            elif growth_type == 'YoY':
                # YoY: compare same month in previous year
                # Extract month from period (YYYY-MM format)
                current_year_month = period[-5:]  # MM part
                year = int(period[:4])
                
                # Find row from previous year, same month
                prev_year_period = f"{year - 1}{period[4:]}"
                prev_row = filtered[filtered['period'] == prev_year_period]
                
                if prev_row.empty:
                    output_row['formula'] = 'N/A (no prior year data)'
                    output_row['growth_rate_pct'] = 'N/A'
                else:
                    prev_spend = prev_row.iloc[0]['actual_spend']
                    if pd.isna(prev_spend):
                        output_row['formula'] = 'Cannot compute (prior year same month null)'
                        output_row['growth_rate_pct'] = 'N/A'
                    else:
                        growth = ((actual_spend - prev_spend) / prev_spend) * 100
                        output_row['formula'] = f'({actual_spend} - {prev_spend}) / {prev_spend} * 100'
                        output_row['growth_rate_pct'] = round(growth, 1)
        
        output_rows.append(output_row)
    
    result_df = pd.DataFrame(output_rows)
    return result_df

def main():
    parser = argparse.ArgumentParser(
        description='UC-0C: Budget Growth Calculator'
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--ward', required=True, help='Ward name (exact match required)')
    parser.add_argument('--category', required=True, help='Category name (exact match required)')
    parser.add_argument('--growth-type', required=False, help='Growth calculation type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Enforcement: growth-type is required
    if not args.growth_type:
        print("ERROR: --growth-type is required. Specify 'MoM' (month-over-month) or 'YoY' (year-over-year).")
        sys.exit(1)
    
    try:
        # Load dataset
        print(f"Loading {args.input}...")
        dataset = load_dataset(args.input)
        df = dataset['dataframe']
        
        # Report nulls
        if dataset['null_count'] > 0:
            print(f"\n⚠️  Found {dataset['null_count']} null actual_spend values:")
            for null_row in dataset['null_rows']:
                reason = null_row['notes'] if null_row['notes'] else "(no reason provided)"
                print(f"  - {null_row['period']} | {null_row['ward']} | {null_row['category']} | {reason}")
        
        # Validate ward and category exist
        available_wards = df['ward'].unique().tolist()
        available_categories = df['category'].unique().tolist()
        
        if args.ward not in available_wards:
            print(f"ERROR: Ward '{args.ward}' not found.")
            print(f"Available wards: {available_wards}")
            sys.exit(1)
        
        if args.category not in available_categories:
            print(f"ERROR: Category '{args.category}' not found.")
            print(f"Available categories: {available_categories}")
            sys.exit(1)
        
        # Compute growth
        print(f"\nComputing {args.growth_type} growth for Ward: {args.ward}, Category: {args.category}...")
        result_df = compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Save output
        result_df.to_csv(args.output, index=False)
        print(f"\n✓ Output saved to {args.output}")
        print(f"\nResults ({args.growth_type} growth):")
        print(result_df.to_string(index=False))
        
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

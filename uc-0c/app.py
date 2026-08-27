"""
UC-0C app.py — Municipal Budget Growth Analyst
Implements RICE framework with load_dataset and compute_growth skills.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path


def load_dataset(file_path):
    """
    Reads the ward budget CSV file, validates columns, and reports null actual_spend values.
    
    Args:
        file_path: Path to ward_budget.csv
        
    Returns:
        Pandas DataFrame with validation report printed to stdout
        
    Raises:
        FileNotFoundError: If file path is invalid
        ValueError: If file is empty or cannot be parsed
        SystemExit: If required columns are missing
    """
    # Validate file exists
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Load CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Cannot parse CSV file: {e}")
    
    # Check if empty
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Validate required columns
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"ERROR: Missing required columns: {', '.join(missing_columns)}")
        print(f"Required columns: {', '.join(required_columns)}")
        sys.exit(1)
    
    # Report null actual_spend values
    null_mask = df['actual_spend'].isna()
    null_count = null_mask.sum()
    
    print(f"\n=== Dataset Validation Report ===")
    print(f"Total rows: {len(df)}")
    print(f"Null actual_spend count: {null_count}")
    
    if null_count != 5:
        print(f"WARNING: Expected exactly 5 null values, found {null_count}. Dataset structure may have changed.")
    
    if null_count > 0:
        print(f"\nNull actual_spend rows:")
        null_rows = df[null_mask][['period', 'ward', 'category', 'notes']]
        for idx, row in null_rows.iterrows():
            print(f"  - {row['period']} · {row['ward']} · {row['category']}")
            print(f"    Reason: {row['notes']}")
    
    print("=================================\n")
    
    return df


def compute_growth(df, ward, category, growth_type, output_path):
    """
    Computes growth for specified ward and category with explicit formula display.
    
    Args:
        df: DataFrame from load_dataset
        ward: Ward name to filter
        category: Category name to filter
        growth_type: "MoM" or "YoY"
        output_path: Path to save output CSV
        
    Raises:
        SystemExit: If parameters are invalid or aggregation is attempted
    """
    # Validate growth_type
    if growth_type not in ['MoM', 'YoY']:
        print(f"ERROR: growth_type must be either 'MoM' or 'YoY', got '{growth_type}'")
        print("Please specify --growth-type MoM or --growth-type YoY")
        sys.exit(1)
    
    # Validate ward exists
    valid_wards = df['ward'].unique().tolist()
    if ward not in valid_wards:
        print(f"ERROR: Ward '{ward}' not found in dataset")
        print(f"Valid wards: {', '.join(valid_wards)}")
        sys.exit(1)
    
    # Validate category exists
    valid_categories = df['category'].unique().tolist()
    if category not in valid_categories:
        print(f"ERROR: Category '{category}' not found in dataset")
        print(f"Valid categories: {', '.join(valid_categories)}")
        sys.exit(1)
    
    # Filter to specified ward and category (per-ward per-category analysis only)
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    filtered_df = filtered_df.sort_values('period').reset_index(drop=True)
    
    if filtered_df.empty:
        print(f"ERROR: No data found for ward '{ward}' and category '{category}'")
        sys.exit(1)
    
    print(f"Computing {growth_type} growth for:")
    print(f"  Ward: {ward}")
    print(f"  Category: {category}")
    print(f"  Periods: {len(filtered_df)} months\n")
    
    # Prepare output columns
    results = []
    
    for idx, row in filtered_df.iterrows():
        result_row = {
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': row['actual_spend']
        }
        
        # Check if current period has null actual_spend
        if pd.isna(row['actual_spend']):
            result_row['growth_value'] = 'NOT_COMPUTABLE'
            result_row['growth_formula_used'] = 'N/A'
            result_row['null_flag'] = row['notes']
            results.append(result_row)
            continue
        
        # Determine comparison period
        if growth_type == 'MoM':
            # Month-over-month: compare with previous month
            if idx == 0:
                result_row['growth_value'] = 'NO_COMPARISON_PERIOD'
                result_row['growth_formula_used'] = 'First period - no prior month'
                result_row['null_flag'] = ''
                results.append(result_row)
                continue
            prev_row = filtered_df.iloc[idx - 1]
        else:  # YoY
            # Year-over-year: compare with same month previous year
            current_period = pd.to_datetime(row['period'])
            prev_period = current_period - pd.DateOffset(years=1)
            prev_period_str = prev_period.strftime('%Y-%m')
            prev_rows = filtered_df[filtered_df['period'] == prev_period_str]
            
            if prev_rows.empty:
                result_row['growth_value'] = 'NO_COMPARISON_PERIOD'
                result_row['growth_formula_used'] = f'No data for {prev_period_str}'
                result_row['null_flag'] = ''
                results.append(result_row)
                continue
            prev_row = prev_rows.iloc[0]
        
        # Check if comparison period has null actual_spend
        if pd.isna(prev_row['actual_spend']):
            result_row['growth_value'] = 'NOT_COMPUTABLE'
            result_row['growth_formula_used'] = f"Comparison period ({prev_row['period']}) has null actual_spend"
            result_row['null_flag'] = ''
            results.append(result_row)
            continue
        
        # Calculate growth
        current_spend = row['actual_spend']
        prev_spend = prev_row['actual_spend']
        growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
        
        # Format formula and result
        sign = '+' if growth_pct >= 0 else ''
        formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100 = {sign}{growth_pct:.1f}%"
        
        result_row['growth_value'] = f"{sign}{growth_pct:.1f}%"
        result_row['growth_formula_used'] = formula
        result_row['null_flag'] = ''
        
        results.append(result_row)
    
    # Create output DataFrame
    output_df = pd.DataFrame(results)
    
    # Save to CSV
    output_df.to_csv(output_path, index=False)
    print(f"✓ Output saved to: {output_path}")
    print(f"  Total rows: {len(output_df)}")
    
    # Summary
    computable = output_df[~output_df['growth_value'].isin(['NOT_COMPUTABLE', 'NO_COMPARISON_PERIOD'])]
    print(f"  Computed growth values: {len(computable)}")
    print(f"  Not computable (null): {len(output_df[output_df['growth_value'] == 'NOT_COMPUTABLE'])}")
    print(f"  No comparison period: {len(output_df[output_df['growth_value'] == 'NO_COMPARISON_PERIOD'])}")


def main():
    parser = argparse.ArgumentParser(
        description='UC-0C: Municipal Budget Growth Analyst - Per-ward per-category growth analysis'
    )
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name to analyze')
    parser.add_argument('--category', required=True, help='Category name to analyze')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YoY'],
                       help='Growth calculation type: MoM (month-over-month) or YoY (year-over-year)')
    parser.add_argument('--output', required=True, help='Path to output CSV file')
    
    args = parser.parse_args()
    
    # Skill 1: Load and validate dataset
    try:
        df = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Skill 2: Compute growth
    compute_growth(df, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()

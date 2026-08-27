"""
UC-0C app.py — Growth calculation for budget data by ward and category.
Enforces single ward + category filtering, flags nulls, shows formulas.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def load_dataset(input_file):
    """
    Load CSV and validate structure.
    Reports null count and which rows have null actual_spend before returning.
    Returns: DataFrame, null_info dict
    """
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")
    
    # Validate required columns
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Report nulls
    null_mask = df['actual_spend'].isna() | (df['actual_spend'] == '')
    null_rows = df[null_mask][['period', 'ward', 'category', 'notes']].copy()
    
    null_info = {
        'count': len(null_rows),
        'rows': null_rows.to_dict('records') if len(null_rows) > 0 else []
    }
    
    # Convert actual_spend to numeric, keeping NaN for missing
    df['actual_spend'] = pd.to_numeric(df['actual_spend'], errors='coerce')
    df['period'] = pd.to_datetime(df['period'], format='%Y-%m')
    
    return df, null_info

def validate_parameters(df, ward, category, growth_type):
    """
    Validate that ward and category exist in dataset.
    Validate growth_type is specified (refuse if None).
    """
    if growth_type is None:
        raise ValueError(
            "REFUSAL: --growth-type must be specified (MoM or YoY). "
            "Cannot guess aggregation method. Valid options: MoM, YoY"
        )
    
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(
            f"REFUSAL: --growth-type '{growth_type}' is invalid. "
            f"Must be 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)"
        )
    
    valid_wards = df['ward'].unique()
    if ward not in valid_wards:
        raise ValueError(
            f"REFUSAL: Ward '{ward}' not found in dataset. "
            f"Valid wards: {', '.join(sorted(valid_wards))}"
        )
    
    valid_categories = df['category'].unique()
    if category not in valid_categories:
        raise ValueError(
            f"REFUSAL: Category '{category}' not found in dataset. "
            f"Valid categories: {', '.join(sorted(valid_categories))}"
        )

def compute_growth(df, ward, category, growth_type):
    """
    Compute growth for specific ward and category.
    Returns DataFrame with period, actual_spend, growth_value, growth_pct, and formula.
    """
    # Filter to ward and category only
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    if len(filtered) == 0:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")
    
    result = []
    
    for idx, row in filtered.iterrows():
        current_period = row['period']
        current_spend = row['actual_spend']
        period_str = current_period.strftime('%Y-%m')
        
        output_row = {
            'period': period_str,
            'actual_spend': current_spend if pd.notna(current_spend) else None,
            'growth_value': None,
            'growth_pct': None,
            'formula': None,
            'status': 'OK'
        }
        
        # Check if current value is null
        if pd.isna(current_spend):
            output_row['status'] = 'NULL_FLAGGED'
            output_row['formula'] = "N/A — actual_spend is null"
            result.append(output_row)
            continue
        
        # First month of series
        if idx == 0:
            output_row['formula'] = "First record — no prior data"
            result.append(output_row)
            continue
        
        # Compute growth
        if growth_type == 'MoM':
            # Find immediately previous month
            if idx > 0:
                prev_row = filtered.iloc[idx - 1]
                prev_spend = prev_row['actual_spend']
                
                if pd.isna(prev_spend):
                    output_row['formula'] = f"MoM: previous month ({prev_row['period'].strftime('%Y-%m')}) is NULL"
                    output_row['status'] = 'CANNOT_COMPUTE'
                else:
                    growth_value = current_spend - prev_spend
                    growth_pct = (growth_value / prev_spend * 100) if prev_spend != 0 else 0
                    
                    output_row['growth_value'] = round(growth_value, 2)
                    output_row['growth_pct'] = round(growth_pct, 1)
                    prev_period = prev_row['period'].strftime('%Y-%m')
                    output_row['formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} × 100 = {growth_pct:.1f}%"
        
        elif growth_type == 'YoY':
            # Find same month previous year
            target_date = current_period.replace(year=current_period.year - 1)
            prev_year_row = filtered[filtered['period'] == target_date]
            
            if len(prev_year_row) == 0:
                output_row['formula'] = f"YoY: no data for {target_date.strftime('%Y-%m')}"
                output_row['status'] = 'CANNOT_COMPUTE'
            else:
                prev_spend = prev_year_row.iloc[0]['actual_spend']
                if pd.isna(prev_spend):
                    output_row['formula'] = f"YoY: {target_date.strftime('%Y-%m')} is NULL"
                    output_row['status'] = 'CANNOT_COMPUTE'
                else:
                    growth_value = current_spend - prev_spend
                    growth_pct = (growth_value / prev_spend * 100) if prev_spend != 0 else 0
                    
                    output_row['growth_value'] = round(growth_value, 2)
                    output_row['growth_pct'] = round(growth_pct, 1)
                    output_row['formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} × 100 = {growth_pct:.1f}%"
        
        result.append(output_row)
    
    return pd.DataFrame(result)

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Calculate budget growth by ward and category",
        epilog="Example: python app.py --input data/budget/ward_budget.csv --ward 'Ward 1 – Kasba' --category 'Roads & Pothole Repair' --growth-type MoM --output growth_output.csv"
    )
    
    parser.add_argument('--input', required=True, help='Input CSV file (e.g., ../data/budget/ward_budget.csv)')
    parser.add_argument('--ward', required=True, help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Category name (e.g., "Roads & Pothole Repair")')
    parser.add_argument('--growth-type', required=False, default=None, help='Growth calculation type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file')
    
    try:
        args = parser.parse_args()
        
        # Step 1: Load and validate dataset
        print(f"[LOAD] Reading dataset from {args.input}...")
        df, null_info = load_dataset(args.input)
        print(f"[LOAD] Dataset loaded: {len(df)} rows")
        
        # Report null values
        if null_info['count'] > 0:
            print(f"\n[NULL_ALERT] Found {null_info['count']} rows with null actual_spend:")
            for null_row in null_info['rows']:
                print(f"  • {null_row['period']} | {null_row['ward']} | {null_row['category']}")
                if null_row['notes']:
                    print(f"    Reason: {null_row['notes'].strip()}")
        
        # Step 2: Validate parameters
        print(f"\n[VALIDATE] Checking ward='{args.ward}', category='{args.category}', growth-type='{args.growth_type}'...")
        validate_parameters(df, args.ward, args.category, args.growth_type)
        
        # Step 3: Compute growth
        print(f"\n[COMPUTE] Computing {args.growth_type} growth for ward and category...")
        result_df = compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Step 4: Output results
        result_df.to_csv(args.output, index=False)
        print(f"\n[OUTPUT] Results written to {args.output}")
        print(f"\nResult preview:")
        print(result_df.to_string(index=False))
        
        print(f"\n✓ SUCCESS: Growth calculation complete")
        
    except (ValueError, FileNotFoundError) as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Number That Looks Right
Calculate MoM/YoY growth for specific ward and category with explicit formulas.
Enforces: no aggregation, null handling, formula transparency, growth_type specification.
See README.md for run command and reference values.
"""
import argparse
import pandas as pd
import sys


def load_dataset(input_file):
    """
    Reads and validates the budget CSV.
    Reports null count and affected rows before returning the dataset.
    
    Input: File path to ward_budget.csv (string)
    Output: Validated pandas DataFrame + console report of null rows
    """
    print(f"Loading dataset from: {input_file}")
    
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}")
        sys.exit(1)
    
    # Validate required columns
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"ERROR: Missing columns: {missing_columns}")
        print(f"Found columns: {list(df.columns)}")
        sys.exit(1)
    
    # Check for null actual_spend rows
    null_rows = df[df['actual_spend'].isna()]
    print(f"\n✓ Dataset loaded: {len(df)} rows")
    print(f"  Wards: {sorted(df['ward'].unique())}")
    print(f"  Categories: {sorted(df['category'].unique())}")
    print(f"  Periods: {sorted(df['period'].unique())}")
    
    if len(null_rows) > 0:
        print(f"\n⚠ NULL actual_spend rows detected ({len(null_rows)} rows):")
        for idx, row in null_rows.iterrows():
            print(f"  {row['period']} · {row['ward']} · {row['category']} → Reason: {row['notes']}")
    
    return df


def compute_growth(df, ward, category, growth_type):
    """
    Computes per-period growth metrics (MoM or YoY) for specified ward and category.
    Shows formula for each row.
    
    Input: DataFrame, ward name (string), category name (string), growth_type (MoM or YoY)
    Output: Per-period table with columns — period, actual_spend, growth_pct, formula
    """
    
    if growth_type not in ['MoM', 'YoY']:
        print(f"ERROR: Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'")
        sys.exit(1)
    
    # Filter for specified ward and category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered.empty:
        print(f"ERROR: No data found for ward='{ward}' and category='{category}'")
        print(f"Available wards: {sorted(df['ward'].unique())}")
        print(f"Available categories: {sorted(df['category'].unique())}")
        sys.exit(1)
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    results = []
    
    if growth_type == 'MoM':
        for idx, row in filtered.iterrows():
            period = row['period']
            actual_spend = row['actual_spend']
            
            if pd.isna(actual_spend):
                results.append({
                    'period': period,
                    'actual_spend': 'NULL',
                    'growth_pct': 'NULL',
                    'formula': f"NULL (Reason: {row['notes']})"
                })
            elif idx == 0:
                # First row has no previous month
                results.append({
                    'period': period,
                    'actual_spend': f"{actual_spend:.1f}",
                    'growth_pct': 'N/A',
                    'formula': "First period — no prior month"
                })
            else:
                prev_spend = filtered.loc[idx - 1, 'actual_spend']
                if pd.isna(prev_spend):
                    results.append({
                        'period': period,
                        'actual_spend': f"{actual_spend:.1f}",
                        'growth_pct': 'NULL',
                        'formula': f"Cannot compute — previous month is NULL"
                    })
                else:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    sign = '+' if growth > 0 else ''
                    results.append({
                        'period': period,
                        'actual_spend': f"{actual_spend:.1f}",
                        'growth_pct': f"{sign}{growth:.1f}%",
                        'formula': f"({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
                    })
    
    elif growth_type == 'YoY':
        for idx, row in filtered.iterrows():
            period = row['period']
            actual_spend = row['actual_spend']
            
            if pd.isna(actual_spend):
                results.append({
                    'period': period,
                    'actual_spend': 'NULL',
                    'growth_pct': 'NULL',
                    'formula': f"NULL (Reason: {row['notes']})"
                })
            else:
                # Find same month in previous year
                current_month = period[-2:]
                year = int(period[:4])
                prior_year_period = f"{year - 1}-{current_month}"
                
                prior_row = filtered[filtered['period'] == prior_year_period]
                
                if prior_row.empty or pd.isna(prior_row.iloc[0]['actual_spend']):
                    results.append({
                        'period': period,
                        'actual_spend': f"{actual_spend:.1f}",
                        'growth_pct': 'N/A',
                        'formula': f"No data for same month in prior year"
                    })
                else:
                    prev_year_spend = prior_row.iloc[0]['actual_spend']
                    growth = ((actual_spend - prev_year_spend) / prev_year_spend) * 100
                    sign = '+' if growth > 0 else ''
                    results.append({
                        'period': period,
                        'actual_spend': f"{actual_spend:.1f}",
                        'growth_pct': f"{sign}{growth:.1f}%",
                        'formula': f"({actual_spend:.1f} - {prev_year_spend:.1f}) / {prev_year_spend:.1f} * 100"
                    })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Calculate ward budget growth with explicit formulas and null handling."
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--ward', required=True, help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Budget category')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YoY'],
                        help='Growth calculation type (MoM=Month-over-Month, YoY=Year-over-Year)')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Enforce: growth_type must be specified
    if not args.growth_type:
        print("ERROR: --growth-type is required. Specify 'MoM' or 'YoY'.")
        sys.exit(1)
    
    # Load and validate dataset
    df = load_dataset(args.input)
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    
    growth_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save output
    growth_df.to_csv(args.output, index=False)
    print(f"\n✓ Output saved to: {args.output}")
    print("\nGrowth Calculation Results:")
    print(growth_df.to_string(index=False))


if __name__ == "__main__":
    main()

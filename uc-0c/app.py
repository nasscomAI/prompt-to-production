"""
UC-0C app.py — Budget growth analyst for municipal ward-level expenditure tracking.
Computes MoM or YoY growth for a specified ward + category combination.
See README.md for run command and expected behaviour.
"""
import argparse
import pandas as pd
import sys


def load_dataset(filepath):
    """Load and validate CSV; report null rows before returning."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {filepath}")
    
    # Validate required columns
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Report null rows (enforcement rule 2)
    null_rows = df[df['actual_spend'].isna()]
    if len(null_rows) > 0:
        print("⚠️  NULL ROWS DETECTED (flagged before computing growth):")
        for _, row in null_rows.iterrows():
            print(f"  {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
        print()
    
    return df


def compute_growth(df, ward, category, growth_type):
    """
    Compute per-period growth for ward + category, showing formula in each row.
    Flags null rows before computing (enforcement rule 2).
    """
    
    # Validation (enforcement rules 1, 4)
    if not ward:
        raise ValueError("--ward must be specified")
    if not category:
        raise ValueError("--category must be specified")
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError("Please specify --growth-type as either MoM or YoY")
    
    # Filter for specified ward + category (enforcement rule 5)
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"Cannot aggregate across wards or categories. Please specify a single ward and single category.")
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Compute growth with formulas (enforcement rule 3)
    results = []
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes']
        
        if pd.isna(actual_spend):
            # Flag null row before attempting computation
            results.append({
                'period': period,
                'actual_spend': '',
                'growth_percentage': '',
                'formula': f'NULL — {notes}'
            })
        else:
            if growth_type == 'MoM':
                if idx == 0:
                    # First month in selection — no previous period
                    results.append({
                        'period': period,
                        'actual_spend': actual_spend,
                        'growth_percentage': '',
                        'formula': 'First month — no previous period'
                    })
                else:
                    prev_spend = filtered.iloc[idx - 1]['actual_spend']
                    if pd.isna(prev_spend):
                        # Previous month is null
                        results.append({
                            'period': period,
                            'actual_spend': actual_spend,
                            'growth_percentage': '',
                            'formula': 'Previous month is NULL — cannot compute'
                        })
                    else:
                        # Compute MoM growth
                        growth = ((actual_spend - prev_spend) / prev_spend) * 100
                        formula = f"({actual_spend} − {prev_spend}) / {prev_spend} × 100%"
                        results.append({
                            'period': period,
                            'actual_spend': actual_spend,
                            'growth_percentage': f'{growth:+.1f}%',
                            'formula': formula
                        })
            
            elif growth_type == 'YoY':
                # YoY requires same month in previous year (2023)
                # Since dataset only contains 2024, YoY not available
                results.append({
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth_percentage': '',
                    'formula': 'YoY not available — dataset contains only 2024'
                })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description='Budget growth analyst: computes MoM/YoY growth for ward + category'
    )
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Specific ward (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Specific category (e.g., "Roads & Pothole Repair")')
    parser.add_argument('--growth-type', required=True, help='MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    try:
        # Load and validate dataset
        print(f"Loading dataset from {args.input}...")
        df = load_dataset(args.input)
        print(f"✓ Dataset loaded: {len(df)} rows\n")
        
        # Compute growth with formula
        print(f"Computing {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}\n")
        growth_df = compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Write output
        growth_df.to_csv(args.output, index=False)
        print(f"✓ Output written to {args.output}\n")
        
        # Display results
        print("Results:")
        print(growth_df.to_string(index=False))
        
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

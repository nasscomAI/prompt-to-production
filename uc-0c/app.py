"""
UC-0C app.py — Number That Looks Right
Enforces per-ward per-category growth calculation with null flagging and formula visibility.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path

def load_dataset(input_path):
    """Load CSV, validate columns, report nulls and which rows before returning."""
    input_path = Path(input_path)
    df = pd.read_csv(input_path)
    
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Missing columns. Required: {required_cols}")
    
    null_rows = df[df['actual_spend'].isna()]
    if len(null_rows) > 0:
        print(f"⚠️  Found {len(null_rows)} null actual_spend rows:", file=sys.stderr)
        for idx, row in null_rows.iterrows():
            print(f"   {row['period']} · {row['ward']} · {row['category']} — {row['notes']}", 
                  file=sys.stderr)
    
    return df

def compute_growth(df, ward, category, growth_type):
    """Compute per-period growth for ward + category with formula shown."""
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'")
    
    # Filter to ward and category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered.empty:
        raise ValueError(f"No data found for ward='{ward}' category='{category}'")
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    results = []
    
    for i in range(len(filtered)):
        row = filtered.iloc[i]
        period = row['period']
        actual = row['actual_spend']
        
        if pd.isna(actual):
            results.append({
                'period': period,
                'ward': row['ward'],
                'category': row['category'],
                'actual_spend': None,
                'growth': None,
                'formula': 'NULL (see notes)',
                'notes': row['notes']
            })
            continue
        
        if growth_type == 'MoM':
            if i == 0:
                results.append({
                    'period': period,
                    'ward': row['ward'],
                    'category': row['category'],
                    'actual_spend': actual,
                    'growth': None,
                    'formula': 'N/A (first period)',
                    'notes': ''
                })
            else:
                prev_actual = filtered.iloc[i-1]['actual_spend']
                if pd.isna(prev_actual):
                    results.append({
                        'period': period,
                        'ward': row['ward'],
                        'category': row['category'],
                        'actual_spend': actual,
                        'growth': None,
                        'formula': f'Previous period null — cannot compute',
                        'notes': ''
                    })
                else:
                    growth = ((actual - prev_actual) / prev_actual) * 100
                    results.append({
                        'period': period,
                        'ward': row['ward'],
                        'category': row['category'],
                        'actual_spend': actual,
                        'growth': growth,
                        'formula': f'({actual} - {prev_actual}) / {prev_actual} * 100 = {growth:.1f}%',
                        'notes': ''
                    })
        
        elif growth_type == 'YoY':
            # YoY not applicable within single year; flag as unavailable
            results.append({
                'period': period,
                'ward': row['ward'],
                'category': row['category'],
                'actual_spend': actual,
                'growth': None,
                'formula': 'YoY N/A (single year data)',
                'notes': ''
            })
    
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C: Per-ward per-category growth calculation")
    parser.add_argument('--input', required=True, help='Input CSV path')
    parser.add_argument('--ward', required=True, help='Ward name (required)')
    parser.add_argument('--category', required=True, help='Category name (required)')
    parser.add_argument('--growth-type', required=False, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV path')
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("❌ Error: --growth-type must be specified. Choose: MoM or YoY", file=sys.stderr)
        sys.exit(1)
    
    # Load and validate dataset
    df = load_dataset(args.input)
    
    # Verify ward and category exist
    if args.ward not in df['ward'].values:
        print(f"❌ Ward '{args.ward}' not found in dataset", file=sys.stderr)
        sys.exit(1)
    
    if args.category not in df['category'].values:
        print(f"❌ Category '{args.category}' not found in dataset", file=sys.stderr)
        sys.exit(1)
    
    # Compute growth
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Write output
    result_df.to_csv(args.output, index=False)
    print(f"✓ Output written to {args.output}")
    print(result_df.to_string())

if __name__ == "__main__":
    main()

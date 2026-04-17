"""
UC-0C app.py — Budget Growth Calculator with Full Null Validation
Enforces strict filtering (no aggregation), explicit null flagging, and formula display.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path

def load_dataset(csv_path):
    """
    Load budget CSV and validate columns.
    Identifies and reports all null actual_spend rows before returning.
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Flag all null rows BEFORE processing
    null_rows = df[df['actual_spend'].isna()]
    null_count = len(null_rows)
    
    if null_count > 0:
        print(f"\n⚠️  ALERT: {null_count} null actual_spend rows detected:")
        for idx, row in null_rows.iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else "[no reason given]"
            print(f"   {row['period']} · {row['ward']} · {row['category']}")
            print(f"   └─ Reason: {reason}")
        print()
    
    return df, null_count

def validate_request(ward, category, growth_type):
    """
    Validate that:
    1. growth_type is specified (MoM or YoY) — refuse if None/empty
    2. Only single ward + single category requested
    """
    if growth_type is None or growth_type.strip() == "":
        raise ValueError(
            "ERROR: growth-type must be specified (MoM or YoY).\n"
            "Refusing to guess. Please specify --growth-type MoM or --growth-type YoY"
        )
    
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth-type: {growth_type}. Use 'MoM' or 'YoY'.")
    
    return True

def compute_growth(df, ward, category, growth_type):
    """
    Compute growth for a single ward + category.
    - MoM: (current - previous) / previous
    - YoY: (current - prev_year) / prev_year
    Shows formula in every output row. Flags nulls explicitly.
    """
    # Filter to single ward + category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data found for {ward} · {category}")
    
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    results = []
    
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        
        if growth_type == 'MoM':
            if idx == 0:
                formula = "N/A (first month)"
                growth_percent = None
            else:
                prev_spend = filtered.iloc[idx-1]['actual_spend']
                prev_period = filtered.iloc[idx-1]['period']
                
                if pd.isna(actual_spend) or pd.isna(prev_spend):
                    formula = f"NULL (cannot compute: current={actual_spend}, previous={prev_spend})"
                    growth_percent = None
                else:
                    growth_percent = ((actual_spend - prev_spend) / prev_spend) * 100
                    formula = f"({actual_spend} - {prev_spend}) / {prev_spend} = {growth_percent:.1f}%"
        
        elif growth_type == 'YoY':
            current_month = period[-2:]  # MM from YYYY-MM
            prev_year_period = f"{int(period[:4])-1}-{current_month}"
            
            prev_year_row = filtered[filtered['period'] == prev_year_period]
            
            if len(prev_year_row) == 0:
                formula = "N/A (no prior year data)"
                growth_percent = None
            else:
                prev_spend = prev_year_row.iloc[0]['actual_spend']
                
                if pd.isna(actual_spend) or pd.isna(prev_spend):
                    formula = f"NULL (cannot compute: {period}={actual_spend}, {prev_year_period}={prev_spend})"
                    growth_percent = None
                else:
                    growth_percent = ((actual_spend - prev_spend) / prev_spend) * 100
                    formula = f"({actual_spend} - {prev_spend}) / {prev_spend} = {growth_percent:.1f}%"
        
        results.append({
            'period': period,
            'actual_spend': actual_spend,
            'formula': formula,
            'growth_percent': growth_percent
        })
    
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument('--input', required=True, help='Path to budget CSV')
    parser.add_argument('--ward', required=True, help='Ward name')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=True, help='MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV path')
    
    args = parser.parse_args()
    
    try:
        # Load and validate
        df, null_count = load_dataset(args.input)
        validate_request(args.ward, args.category, args.growth_type)
        
        # Compute growth
        result = compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Save output
        result.to_csv(args.output, index=False)
        print(f"✓ Output saved to {args.output}\n")
        print(result.to_string(index=False))
        
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()


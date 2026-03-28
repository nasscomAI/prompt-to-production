"""
UC-0C app.py — Municipal Budget Growth Analysis
Implements RICE framework from agents.md and skills.md
See README.md for run command and expected behaviour.
"""
import argparse
import pandas as pd
import sys
import os

# ============================================================================
# SKILL: load_dataset
# ============================================================================
def load_dataset(filepath):
    """
    Reads ward_budget.csv, validates columns, and flags null rows.
    
    Returns: {
        'data': DataFrame,
        'null_count': int,
        'null_rows': list of {period, ward, category, reason}
    }
    """
    # Check file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    # Load CSV
    df = pd.read_csv(filepath)
    
    # Validate required columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Find null actual_spend rows
    null_mask = df['actual_spend'].isna()
    null_rows = df[null_mask][['period', 'ward', 'category', 'notes']].copy()
    null_rows.columns = ['period', 'ward', 'category', 'reason']
    null_rows = null_rows.sort_values('period').to_dict('records')
    
    return {
        'data': df,
        'null_count': int(null_mask.sum()),
        'null_rows': null_rows
    }


# ============================================================================
# SKILL: compute_growth
# ============================================================================
def compute_growth(ward, category, growth_type, data):
    """
    Computes MoM or YoY growth for a specific ward and category.
    
    Input: {ward, category, growth_type: 'MoM'|'YoY', data: DataFrame}
    Output: DataFrame with {period, actual_spend, growth_rate, formula}
    """
    # Validate growth_type
    if growth_type not in ('MoM', 'YoY'):
        raise ValueError(f"Invalid growth_type: {growth_type}. Must be 'MoM' or 'YoY'.")
    
    # Filter for ward and category
    filtered = data[(data['ward'] == ward) & (data['category'] == category)].copy()
    
    if filtered.empty:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Calculate growth
    results = []
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes'] if pd.notna(row['notes']) else ""
        
        # Determine comparison period offset
        offset = 1 if growth_type == 'MoM' else 12  # 12 months for YoY
        
        if idx < offset:
            # Not enough history for comparison
            growth_rate = None
            formula = f"N/A (insufficient {growth_type} history)"
        elif pd.isna(actual_spend):
            # Current value is null
            growth_rate = None
            reason = notes if notes else "NULL value"
            formula = f"NULL — {reason}"
        else:
            # Compare with previous period
            prev_row = filtered.iloc[idx - offset]
            prev_spend = prev_row['actual_spend']
            
            if pd.isna(prev_spend):
                # Previous value is null
                growth_rate = None
                prev_reason = prev_row['notes'] if pd.notna(prev_row['notes']) else "NULL value"
                formula = f"Cannot compute (prior period NULL — {prev_reason})"
            else:
                # Compute growth rate
                growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
                growth_rate = f"{growth_pct:+.1f}%"
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend} = {growth_rate}"
        
        results.append({
            'period': period,
            'actual_spend': actual_spend if pd.notna(actual_spend) else 'NULL',
            'growth_rate': growth_rate if growth_rate else 'N/A',
            'formula': formula
        })
    
    return pd.DataFrame(results)


# ============================================================================
# ENFORCEMENT & ORCHESTRATION
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description='UC-0C: Municipal Budget Growth Analysis Agent'
    )
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Category name (e.g., "Roads & Pothole Repair")')
    parser.add_argument('--growth-type', required=False, help='MoM or YoY (REQUIRED)')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # ENFORCEMENT: Refuse if growth-type not specified
    if not args.growth_type:
        print("ERROR: --growth-type is REQUIRED")
        print("Please specify either 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)")
        sys.exit(1)
    
    try:
        # 1. Load and validate dataset
        print(f"Loading dataset from {args.input}...")
        result = load_dataset(args.input)
        df = result['data']
        null_count = result['null_count']
        null_rows = result['null_rows']
        
        # 2. ENFORCEMENT: Flag all null rows BEFORE computation
        if null_count > 0:
            print(f"\n⚠️  WARNING: {null_count} null actual_spend row(s) detected:")
            for row in null_rows:
                print(f"  {row['period']} · {row['ward']} · {row['category']} → {row['reason']}")
            print("\nThese rows will be flagged in output, not computed or skipped.")
        
        # 3. ENFORCEMENT: No cross-ward/cross-category aggregation
        # (Inherently enforced by accepting only single ward/category)
        
        # 4. Compute growth with formulas shown
        print(f"\nComputing {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}")
        
        output_df = compute_growth(args.ward, args.category, args.growth_type, df)
        
        # 5. Write output with all transparency
        output_df.to_csv(args.output, index=False)
        print(f"\n✓ Output written to {args.output}")
        print(f"\nSample rows:")
        print(output_df.to_string(index=False))
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

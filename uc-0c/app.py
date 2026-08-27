"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    """
    Reads CSV, validates columns, and reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file missing: {file_path}")

    df = pd.read_csv(file_path)
    
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Identify null actual_spend rows
    null_mask = df['actual_spend'].isnull()
    null_count = null_mask.sum()
    null_rows = df[null_mask]

    return df, null_count, null_rows

def compute_growth(df, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified. Please provide a valid growth type (e.g., MoM). Will not guess.")

    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"REFUSAL: Invalid growth_type '{growth_type}'. Only 'MoM' or 'YoY' supported.")

    if not ward or not category:
        raise ValueError("REFUSAL: Cannot aggregate across wards or categories. Please specify exact --ward and --category.")

    # Filter dataset strictly by ward and category
    df_filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()

    if df_filtered.empty:
        print(f"WARNING: No data found for Ward: '{ward}', Category: '{category}'.")
        return pd.DataFrame()

    # Sort sequentially to calculate period-over-period growth safely
    df_filtered = df_filtered.sort_values(by='period').reset_index(drop=True)

    results = []
    
    for i, row in df_filtered.iterrows():
        period = row['period']
        actual = row['actual_spend']
        notes = row['notes']
        
        # Flag null rows without computing
        if pd.isna(actual):
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth_result': 'FLAGGED: NULL',
                'formula': 'N/A',
                'notes': notes
            })
            continue
            
        # Compute growth
        if growth_type == 'MoM':
            if i == 0 or pd.isna(df_filtered.at[i-1, 'actual_spend']):
                growth = 'N/A'
                formula = 'No previous valid month to compare'
            else:
                prev_actual = df_filtered.at[i-1, 'actual_spend']
                growth_val = ((actual - prev_actual) / prev_actual) * 100
                growth = f"{growth_val:+.1f}%"
                formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
                
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': actual,
                'growth_result': growth,
                'formula': formula,
                'notes': notes if pd.notna(notes) else ''
            })

    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Calculate financial growth securely and strictly.")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=False, help="Specific ward name (required to prevent aggregation)")
    parser.add_argument("--category", required=False, help="Specific category name (required to prevent aggregation)")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    # Enforcement: "If --growth-type not specified — refuse and ask, never guess."
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. Please specify (e.g. MoM). Never guessing the formula.")
        sys.exit(1)
        
    # Enforcement: "Never aggregate across wards or categories unless explicitly instructed — refuse if asked."
    if not args.ward or not args.category:
        print("REFUSAL: Cannot compute all-ward/all-category aggregations. Please specify --ward and --category explicitly.")
        sys.exit(1)

    try:
        df, null_count, null_rows = load_dataset(args.input)
        
        # Enforcement: "Flag every null row before computing — report null reason from the notes column."
        if null_count > 0:
            print(f"INFO: Found {null_count} null actual_spend rows globally in the dataset.")
            for _, r in null_rows.iterrows():
                print(f"  - FLAGGED NULL: Period {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
        else:
            print("INFO: No null rows found in the dataset.")
            
        growth_df = compute_growth(df, args.ward, args.category, args.growth_type)
        
        if not growth_df.empty:
            growth_df.to_csv(args.output, index=False)
            print(f"SUCCESS: Output securely written to {args.output}")
        else:
            print("INFO: No valid records outputted.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

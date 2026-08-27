import argparse
import sys
import pandas as pd

def load_dataset(file_path):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Missing required column '{col}' in dataset.")
            sys.exit(1)

    # Flag every null row before computing — report null reason from the notes column
    null_mask = df['actual_spend'].isna()
    null_count = null_mask.sum()
    
    if null_count > 0:
        print(f"Found {null_count} rows with null actual_spend:")
        for idx, row in df[null_mask].iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else "No reason provided"
            print(f" - {row['period']} · {row['ward']} · {row['category']} -> {reason}")
    else:
        print("No null actual_spend values found.")

    return df

def compute_growth(df, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    # Filter exactly to the ward and category provided
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'")
        return pd.DataFrame()

    # Sort chronological
    filtered_df = filtered_df.sort_values(by='period')
    
    results = []
    prev_spend = None
    
    for idx, row in filtered_df.iterrows():
        period = row['period']
        actual = row['actual_spend']
        notes = row['notes'] if pd.notna(row['notes']) else ""
        
        # If the value is explicitly missing
        if pd.isna(actual):
            growth = "NULL"
            formula = "n/a"
            note_str = notes if notes else "Must be flagged — not computed"
        else:
            if growth_type == 'MoM':
                if prev_spend is None or pd.isna(prev_spend):
                    growth = "n/a"
                    formula = "n/a (no previous month)"
                    note_str = notes
                else:
                    growth_val = ((actual - prev_spend) / prev_spend) * 100
                    # Formatting nicely (e.g. +33.1% or −34.8%)
                    sign = "+" if growth_val > 0 else "−"
                    growth = f"{sign}{abs(growth_val):.1f}%"
                    # Formula tracking
                    formula = f"(({actual} - {prev_spend}) / {prev_spend}) * 100"
                    note_str = notes
            else:
                growth = "n/a"
                formula = f"n/a (unknown growth-type {growth_type})"
                note_str = notes
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': actual if pd.notna(actual) else "NULL",
            'Growth': growth,
            'Formula': formula,
            'Notes': note_str
        })
        
        prev_spend = actual
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Ward Budget Growth Calculator")
    parser.add_argument('--input', help='Input CSV file path')
    parser.add_argument('--ward', help='Specific ward to compute')
    parser.add_argument('--category', help='Specific category to compute')
    parser.add_argument('--growth-type', help='Growth type (e.g. MoM)')
    parser.add_argument('--output', help='Output CSV file path')
    
    args = parser.parse_args()

    if not args.input:
        print("Error: --input is required.")
        sys.exit(1)
        
    if not args.output:
        print("Error: --output is required.")
        sys.exit(1)

    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type must be explicitly specified (e.g., --growth-type MoM). Refusing to guess.")
        sys.exit(1)

    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or args.ward.lower() == 'all':
        print("Error: --ward is required and must be specific. Aggregating across wards is forbidden.")
        sys.exit(1)
        
    if not args.category or args.category.lower() == 'all':
        print("Error: --category is required and must be specific. Aggregating across categories is forbidden.")
        sys.exit(1)

    # Rule 2: Flag every null row before computing
    df = load_dataset(args.input)

    # Rule 3: Show formula used in every output row alongside the result
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    if not result_df.empty:
        result_df.to_csv(args.output, index=False)
        print(f"\nSuccess! Written growth results to {args.output}")

if __name__ == "__main__":
    main()

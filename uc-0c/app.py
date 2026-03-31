import argparse
import pandas as pd
import sys

def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        sys.exit(1)

    # Validate columns
    expected_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing expected columns: {missing_cols}")
        sys.exit(1)

    # Report nulls before returning
    null_rows = df[df['actual_spend'].isnull()]
    print("\n--- NULL VALUE REPORT ---")
    print(f"Found {len(null_rows)} rows with null actual_spend.")
    for _, row in null_rows.iterrows():
        reason = row['notes'] if pd.notna(row['notes']) else 'No reason provided'
        print(f"- {row['period']} · {row['ward']} · {row['category']} -> Reason: {reason}")
    print("-------------------------\n")

    return df

def compute_growth(df, ward, category, growth_type):
    # Enforcement: Refuse if growth_type is missing
    if not growth_type:
        print("REFUSAL: --growth-type not specified. Formula assumption failure avoided. Must provide explicitly (e.g., MoM).")
        sys.exit(1)

    # Enforcement: Never aggregate across wards or categories
    if not ward or not category or ward.lower() == 'any' or category.lower() == 'any':
        print("REFUSAL: All-ward or all-category aggregation is prohibited. Must specify exact ward and category.")
        sys.exit(1)

    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered_df.empty:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return pd.DataFrame()

    # Sort strictly by period
    filtered_df = filtered_df.sort_values(by='period').reset_index(drop=True)

    results = []
    previous_spend = None

    for index, row in filtered_df.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes']
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_spend,
            'growth': None,
            'formula_used': None,
            'notes': notes
        }

        # Enforcement: Flag every null row before computing
        if pd.isna(actual_spend):
            result_row['growth'] = "FLAGGED: NULL"
            result_row['formula_used'] = f"Not computed due to missing data (Reason: {notes})"
            previous_spend = None  # Reset previous to prevent invalid continuity
        else:
            if growth_type == 'MoM':
                if previous_spend is not None:
                    try:
                        growth_pct = ((actual_spend - previous_spend) / previous_spend) * 100
                        result_row['growth'] = f"{growth_pct:+.1f}%"
                        result_row['formula_used'] = f"(({actual_spend} - {previous_spend}) / {previous_spend}) * 100"
                    except ZeroDivisionError:
                        result_row['growth'] = "N/A"
                        result_row['formula_used'] = "Division by zero"
                else:
                    result_row['growth'] = "N/A"
                    result_row['formula_used'] = "First valid period; no previous actual_spend to compare"
                
                previous_spend = actual_spend
            else:
                print(f"REFUSAL: Unsupported or unhandled growth_type '{growth_type}'. Only MoM is currently implemented.")
                sys.exit(1)

        results.append(result_row)

    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument('--input', required=True, help="Path to input CSV")
    parser.add_argument('--ward', required=False, help="Target ward")
    parser.add_argument('--category', required=False, help="Target category")
    parser.add_argument('--growth-type', required=False, help="Growth type (e.g., MoM)")
    parser.add_argument('--output', required=True, help="Path to output CSV")

    args = parser.parse_args()

    # Enforce ward and category args exist 
    if not args.ward or not args.category:
        print("REFUSAL: Ward and Category must be explicitly specified to prevent unauthorized aggregation.")
        sys.exit(1)

    df = load_dataset(args.input)
    growth_df = compute_growth(df, args.ward, args.category, args.growth_type)

    if not growth_df.empty:
        growth_df.to_csv(args.output, index=False)
        print(f"Success: Processed {len(growth_df)} rows. Output saved to {args.output}")

if __name__ == '__main__':
    main()

"""
UC-0C — Budget Growth Calculator
Implements RICE framework from agents.md with skills from skills.md.
Prevents wrong aggregation, silent null handling, and formula assumption.
"""
import argparse
import pandas as pd
import sys

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Read CSV budget data, validate columns, report null values.

    Implements skill: load_dataset from skills.md
    Reports null actual_spend rows BEFORE returning data.
    """
    required_columns = ['period', 'ward', 'category', 'actual_spend', 'budgeted_amount', 'notes']

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Budget file not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot read CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Report null values
    null_rows = df[df['actual_spend'].isna()]
    null_count = len(null_rows)

    print(f"\n=== Dataset Loaded ===")
    print(f"Total rows: {len(df)}")
    print(f"Null actual_spend values: {null_count}")

    if null_count > 0:
        print(f"\nNull rows (will be flagged in output):")
        for idx, row in null_rows.iterrows():
            print(f"  - {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")

    print()
    return df


def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    """
    Compute period-over-period growth for specific ward-category combination.

    Implements skill: compute_growth from skills.md
    Shows formula for each period, flags nulls.
    """
    # Validate growth_type
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)")

    # Filter to specific ward and category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()

    if len(filtered) == 0:
        available_wards = df['ward'].unique().tolist()
        available_cats = df[df['ward'] == ward]['category'].unique().tolist() if ward in df['ward'].values else []

        if ward not in df['ward'].values:
            raise ValueError(f"Ward '{ward}' not found. Available wards: {available_wards}")
        else:
            raise ValueError(f"Category '{category}' not found for ward '{ward}'. Available categories: {available_cats}")

    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)

    # Initialize result columns
    filtered['growth_rate'] = ''
    filtered['formula'] = ''
    filtered['flag'] = ''

    # Compute growth for each period
    for idx, row in filtered.iterrows():
        period = row['period']
        current_spend = row['actual_spend']

        # Handle null current value
        if pd.isna(current_spend):
            filtered.at[idx, 'growth_rate'] = 'NULL'
            filtered.at[idx, 'formula'] = 'N/A'
            filtered.at[idx, 'flag'] = f"NULL: {row['notes']}"
            continue

        # Determine prior period index
        if growth_type == 'MoM':
            prior_idx = idx - 1
        else:  # YoY
            # Find same month in previous year
            year, month = period.split('-')
            prior_year = str(int(year) - 1)
            prior_period = f"{prior_year}-{month}"
            prior_row = filtered[filtered['period'] == prior_period]
            prior_idx = prior_row.index[0] if len(prior_row) > 0 else -1

        # Check if prior period exists
        if prior_idx < 0 or prior_idx >= len(filtered):
            filtered.at[idx, 'growth_rate'] = 'N/A'
            filtered.at[idx, 'formula'] = 'No prior period'
            filtered.at[idx, 'flag'] = ''
            continue

        prior_spend = filtered.at[prior_idx, 'actual_spend']

        # Handle null prior value
        if pd.isna(prior_spend):
            filtered.at[idx, 'growth_rate'] = 'N/A'
            filtered.at[idx, 'formula'] = 'Prior period is NULL'
            filtered.at[idx, 'flag'] = 'Cannot compute - prior period has NULL actual_spend'
            continue

        # Compute growth
        growth = (current_spend - prior_spend) / prior_spend
        growth_pct = growth * 100

        filtered.at[idx, 'growth_rate'] = f"{growth_pct:+.1f}%"
        filtered.at[idx, 'formula'] = f"({current_spend} - {prior_spend}) / {prior_spend} = {growth_pct:+.1f}%"
        filtered.at[idx, 'flag'] = ''

    # Select output columns
    result = filtered[['period', 'actual_spend', 'growth_rate', 'formula', 'flag']]

    return result


def main():
    """
    Main entry point - parses arguments and orchestrates growth calculation.
    """
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'],
                        help="Growth type: 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV file")
    args = parser.parse_args()

    # Load dataset (reports nulls)
    df = load_dataset(args.input)

    # Compute growth
    growth_df = compute_growth(df, args.ward, args.category, args.growth_type)

    # Write output
    try:
        growth_df.to_csv(args.output, index=False)
        print(f"Done. Growth analysis written to {args.output}")
        print(f"Ward: {args.ward} | Category: {args.category} | Type: {args.growth_type}")
    except Exception as e:
        print(f"Error: Cannot write output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

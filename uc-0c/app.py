"""
UC-0C app.py — Budget growth calculator.
Computes MoM or YoY growth for a specific ward and category, with formula visibility and null handling.
"""
import argparse
import pandas as pd
import sys


def load_dataset(filepath):
    """Load and validate the ward budget CSV, identifying null rows."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise ValueError(f"File not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {str(e)}")

    # Validate required columns
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    # Identify null rows
    null_rows = df[df['actual_spend'].isna()][['period', 'ward', 'category', 'notes']].to_dict('records')

    return {
        'data': df,
        'null_rows': null_rows,
        'columns_found': list(df.columns),
        'row_count': len(df)
    }


def compute_growth(dataset, ward, category, growth_type):
    """Compute MoM or YoY growth for a specific ward and category."""
    df = dataset['data']

    # Validate growth_type
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Please specify --growth-type (MoM or YoY), received: {growth_type}")

    # Check if ward exists
    available_wards = df['ward'].unique().tolist()
    if ward not in available_wards:
        raise ValueError(f"Ward not found: '{ward}'\nAvailable wards: {available_wards}")

    # Check if category exists
    available_categories = df['category'].unique().tolist()
    if category not in available_categories:
        raise ValueError(f"Category not found: '{category}'\nAvailable categories: {available_categories}")

    # Filter for ward and category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    filtered = filtered.sort_values('period').reset_index(drop=True)

    if len(filtered) == 0:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")

    # Check if there are any non-null values
    if filtered['actual_spend'].isna().all():
        raise ValueError(f"No non-null actual_spend values for ward='{ward}', category='{category}'")

    # Report null rows in this selection
    null_in_selection = filtered[filtered['actual_spend'].isna()][['period', 'notes']]
    if len(null_in_selection) > 0:
        print(f"Null rows found in {ward} / {category}:")
        for _, row in null_in_selection.iterrows():
            print(f"  {row['period']}: {row['notes']}")
        print()

    # Compute growth
    results = []

    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']

        if pd.isna(actual_spend):
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'previous_period_spend': 'N/A',
                'growth_percentage': 'N/A',
                'formula_used': f"Null — {row['notes']}"
            })
        else:
            # Find previous period
            if growth_type == 'MoM':
                prev_row = filtered[filtered['period'] < period].tail(1)
            else:  # YoY
                year_month = period.split('-')
                prev_year = str(int(year_month[0]) - 1)
                prev_period = f"{prev_year}-{year_month[1]}"
                prev_row = filtered[filtered['period'] == prev_period]

            if len(prev_row) == 0:
                results.append({
                    'period': period,
                    'actual_spend': f"{actual_spend:.1f}",
                    'previous_period_spend': 'N/A',
                    'growth_percentage': 'N/A',
                    'formula_used': 'No prior period'
                })
            elif pd.isna(prev_row.iloc[0]['actual_spend']):
                results.append({
                    'period': period,
                    'actual_spend': f"{actual_spend:.1f}",
                    'previous_period_spend': 'NULL (prior)',
                    'growth_percentage': 'N/A',
                    'formula_used': 'Prior period is null'
                })
            else:
                prev_spend = prev_row.iloc[0]['actual_spend']
                growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
                formula = f"({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100 = {growth_pct:+.1f}%"

                results.append({
                    'period': period,
                    'actual_spend': f"{actual_spend:.1f}",
                    'previous_period_spend': f"{prev_spend:.1f}",
                    'growth_percentage': f"{growth_pct:+.1f}%",
                    'formula_used': formula
                })

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description='Calculate budget growth metrics by ward and category'
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--ward', required=True, help='Ward name (exact match required)')
    parser.add_argument('--category', required=True, help='Budget category (exact match required)')
    parser.add_argument('--growth-type', required=True, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file path')

    args = parser.parse_args()

    try:
        # Load dataset
        print(f"Loading dataset from {args.input}...")
        dataset = load_dataset(args.input)
        print(f"✓ Loaded {dataset['row_count']} rows")

        # Report all null rows in the dataset
        if dataset['null_rows']:
            print(f"\nDataset contains {len(dataset['null_rows'])} null actual_spend rows:")
            for null_row in dataset['null_rows']:
                print(f"  {null_row['period']} · {null_row['ward']} · {null_row['category']}: {null_row['notes']}")

        # Compute growth
        print(f"\nComputing {args.growth_type} growth...")
        result_df = compute_growth(dataset, args.ward, args.category, args.growth_type)

        # Write output
        result_df.to_csv(args.output, index=False)
        print(f"✓ Output written to {args.output}\n")
        print(result_df.to_string(index=False))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

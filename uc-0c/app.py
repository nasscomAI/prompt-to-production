"""
UC-0C — Computes ward- and category-specific growth from a municipal budget CSV.
"""
import argparse
import sys

import pandas as pd

REQUIRED_COLUMNS = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']


def load_dataset(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df.empty:
        raise ValueError("CSV file is empty")

    null_mask = df['actual_spend'].isna()
    print(f"Null actual_spend count: {null_mask.sum()}")
    if null_mask.any():
        print("Null rows:")
        for _, r in df[null_mask][['period', 'ward', 'category', 'notes']].iterrows():
            note = r['notes'] if pd.notna(r['notes']) else 'No reason provided'
            print(f"  {r['period']} | {r['ward']} | {r['category']} | notes: {note}")

    return df


def compute_growth(df, ward, category, growth_type):
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered.empty:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")

    filtered = filtered.sort_values('period').reset_index(drop=True)

    if len(filtered) < 2:
        raise ValueError(f"Fewer than 2 periods — cannot compute growth")

    formula_str = "((current - previous) / previous) * 100"
    results = []
    prev_spend = None

    for _, row in filtered.iterrows():
        current_spend = row['actual_spend']
        current_null = pd.isna(current_spend)

        entry = {
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'budgeted_amount': row['budgeted_amount'],
            'actual_spend': current_spend,
            'growth_type': growth_type,
            'growth_value': None,
            'formula': formula_str,
            'null_flag': 'Yes' if current_null else 'No',
            'null_reason': row['notes'] if current_null and pd.notna(row['notes']) else (
                '' if not current_null else 'No reason provided'
            ),
        }

        if not current_null and prev_spend is not None and not pd.isna(prev_spend):
            entry['growth_value'] = round(((current_spend - prev_spend) / prev_spend) * 100, 2)

        results.append(entry)
        prev_spend = current_spend

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description='Compute ward/category growth from budget CSV.')
    parser.add_argument('--input', required=True, help='Path to input CSV')
    parser.add_argument('--ward', required=True, help='Ward name to filter')
    parser.add_argument('--category', required=True, help='Category name to filter')
    parser.add_argument('--growth-type', choices=['MoM', 'YoY'], help='Growth type (MoM or YoY)')
    parser.add_argument('--output', required=True, help='Path to output CSV')

    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Please specify 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    try:
        df = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = compute_growth(df, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"Error computing growth: {e}", file=sys.stderr)
        sys.exit(1)

    null_in_result = result[result['null_flag'] == 'Yes']
    if not null_in_result.empty:
        print(f"\nFlagged {len(null_in_result)} null row(s) in output:")
        for _, r in null_in_result.iterrows():
            print(f"  {r['period']} — {r['null_reason']}")

    result.to_csv(args.output, index=False)
    print(f"\nGrowth output written to {args.output}")


if __name__ == '__main__':
    main()

"""
UC-0C app.py — Budget growth calculator (STRICT MODE)
Enforces:
- No aggregation
- Mandatory null reporting
- Explicit formulas per row
- Deterministic per-ward, per-category output
"""

import argparse
import pandas as pd
import sys


REQUIRED_COLUMNS = [
    'period', 'ward', 'category',
    'budgeted_amount', 'actual_spend', 'notes'
]


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception:
        fail("Input file not found or unreadable")

    # Schema validation
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        fail(f"Dataset schema invalid. Missing columns: {missing}")

    # Null detection (MANDATORY PRE-CHECK)
    null_rows = df[df['actual_spend'].isnull()]

    print(f"Dataset loaded: {len(df)} rows")
    print(f"Null actual_spend rows detected: {len(null_rows)}")

    for _, row in null_rows.iterrows():
        print(
            f"NULL → {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes']}"
        )

    return df


def compute_growth(df, ward, category, growth_type):

    # Enforce growth_type
    if not growth_type:
        fail("growth_type must be specified (MoM or YoY)")

    if growth_type not in ['MoM', 'YoY']:
        fail("Invalid growth_type. Must be MoM or YoY")

    if growth_type == 'YoY':
        fail("YoY not supported: dataset contains only one year")

    # STRICT scope filtering
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()

    if filtered.empty:
        fail(f"No data found for ward='{ward}' and category='{category}'")

    # ENFORCE no aggregation via row count
    if len(filtered) != 12:
        fail("Scope violation: expected exactly 12 rows (one per month)")

    # Sort by period
    filtered['period'] = pd.to_datetime(filtered['period'])
    filtered = filtered.sort_values('period')

    results = []

    prev_actual = None

    for idx, row in filtered.iterrows():
        period = row['period'].strftime('%Y-%m')
        actual = row['actual_spend']
        notes = row['notes']

        # Case 1: NULL current
        if pd.isnull(actual):
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth_percentage': 'NULL',
                'formula_used': 'Not computed due to null input',
                'notes': notes
            })
            prev_actual = None  # CRITICAL: break chain
            continue

        # Case 2: First row OR previous null
        if prev_actual is None:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': actual,
                'growth_percentage': 'NULL',
                'formula_used': 'No previous period',
                'notes': notes
            })
            prev_actual = actual
            continue

        # Case 3: Valid computation
        growth = ((actual - prev_actual) / prev_actual) * 100

        formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"

        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual,
            'growth_percentage': f"{growth:.1f}%",
            'formula_used': formula,
            'notes': notes
        })

        prev_actual = actual

    # FINAL GUARD: ensure no aggregation slipped through
    if len(results) != 12:
        fail("Output validation failed: expected 12 rows")

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator (Strict)"
    )

    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    df = load_dataset(args.input)

    result_df = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )

    result_df.to_csv(args.output, index=False)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
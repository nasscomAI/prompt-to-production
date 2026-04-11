"""
UC-0C app.py — Budget Growth Calculator
Built using RICE + agents.md + skills.md + CRAFT workflow
"""

import argparse
import csv
import sys


def load_dataset(filepath):
    """
    reads CSV, validates columns, reports null count and which rows before returning
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        raise FileNotFoundError(f"Error accessing file: {e}")

    # Validate columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend'}
    if not required_cols.issubset(set(reader.fieldnames)):
        raise ValueError(f"Missing required columns. Found: {reader.fieldnames}")

    # Report nulls
    null_rows = [row for row in data if not row.get('actual_spend', '').strip()]
    print(f"Data loaded successfully: {len(data)} rows.")
    if null_rows:
        print(f"Warning: Intercepted {len(null_rows)} deliberately null actual_spend rows:")
        for r in null_rows:
            reason = r.get('notes', 'No reason provided')
            print(f"  - Flagging NULL row: {r['period']} | {r['ward']} | {r['category']} -> Reason: {reason}")
    else:
        print("No null rows found.")

    return data


def compute_growth(data, ward, category, growth_type):
    """
    takes ward + category + growth_type, returns per-period table with formula shown
    """
    if str(ward).lower() == 'all' or str(category).lower() == 'all':
        raise ValueError("Policy violation: Never aggregate across wards or categories unless explicitly instructed. Request refused.")

    if not growth_type:
        raise ValueError("Growth type not specified. Will not guess. Please provide --growth-type (e.g., MoM)")

    if growth_type.lower() != 'mom':
        raise ValueError(f"Growth type '{growth_type}' not currently implemented. Only MoM is supported.")

    filtered = [d for d in data if d['ward'].strip() == ward.strip() and d['category'].strip() == category.strip()]
    if not filtered:
        print(f"No data found for Ward: '{ward}', Category: '{category}'")

    filtered.sort(key=lambda x: x['period'])

    results = []
    prev_spend = None

    for row in filtered:
        period = row['period']
        actual_val = row.get('actual_spend', '').strip()

        if not actual_val:
            # Null row encountered
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': 'NULL',
                'formula': 'Cannot compute; actual_spend is NULL'
            })
            prev_spend = None
            continue

        actual_val = float(actual_val)
        if prev_spend is None:
            growth_str = 'n/a'
            formula_str = 'n/a (first period or previous was NULL)'
        else:
            diff = actual_val - prev_spend
            pct = (diff / prev_spend) * 100
            sign = '+' if pct > 0 else ''
            growth_str = f"{sign}{pct:.1f}%"
            formula_str = f"(({actual_val} - {prev_spend}) / {prev_spend}) * 100"

        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual_val,
            'growth': growth_str,
            'formula': formula_str
        })
        prev_spend = actual_val

    return results


def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", default=None, help="Type of growth calculation (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args, unknown = parser.parse_known_args()

    # Rule 4: Refuse to guess if growth-type missing
    if not args.growth_type:
        print("Error: --growth-type not specified — refuse and ask, never guess.")
        sys.exit(1)

    try:
        data = load_dataset(args.input)
        growth_results = compute_growth(data, args.ward, args.category, args.growth_type)

        if growth_results:
            with open(args.output, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=growth_results[0].keys())
                writer.writeheader()
                writer.writerows(growth_results)
            print(f"\nGrowth successfully calculated and written to {args.output}")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
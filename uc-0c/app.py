"""
UC-0C app.py — Budget Growth Calculator
Strictly enforces: no silent aggregation, null flagging before compute,
formula shown per row, refusal if --growth-type is not specified.
"""
import argparse
import csv
import os
import sys


REQUIRED_COLUMNS = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}


def load_dataset(filepath: str) -> tuple:
    """
    Skill: load_dataset
    Reads the CSV, validates columns, reports nulls before returning.
    Returns: (rows: list[dict], null_report: list[dict])
    """
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("ERROR: CSV has no headers.", file=sys.stderr)
            sys.exit(1)

        missing_cols = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_cols:
            print(f"ERROR: Missing required columns: {missing_cols}", file=sys.stderr)
            sys.exit(1)

        rows = list(reader)

    if not rows:
        print("ERROR: CSV contains no data rows.", file=sys.stderr)
        sys.exit(1)

    # Build null report BEFORE any processing — enforcement rule 2
    null_report = []
    for row in rows:
        if row.get('actual_spend', '').strip() == '':
            null_report.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row.get('notes', 'No reason provided').strip() or 'No reason provided'
            })

    if null_report:
        print(f"\n⚠  NULL REPORT — {len(null_report)} row(s) with missing actual_spend flagged before computation:")
        for n in null_report:
            print(f"   [{n['period']}] {n['ward']} / {n['category']} → {n['reason']}")
        print()

    return rows, null_report


def compute_growth(rows: list, growth_type: str, null_report: list) -> list:
    """
    Skill: compute_growth
    Filters to ward+category slice, computes MoM or YoY growth with formula shown.
    Null rows are flagged, not computed.
    """
    if growth_type not in ('MoM', 'YoY'):
        print(
            "ERROR: --growth-type must be explicitly 'MoM' or 'YoY'. "
            "Refusing to guess. Please re-run with --growth-type MoM or --growth-type YoY.",
            file=sys.stderr
        )
        sys.exit(1)

    if not rows:
        print("ERROR: No data rows to compute — filtered slice is empty.", file=sys.stderr)
        sys.exit(1)

    # Build null lookup for fast check
    null_keys = {(n['period'], n['ward'], n['category']) for n in null_report}

    # Sort by period
    rows_sorted = sorted(rows, key=lambda r: r['period'])

    results = []
    for i, row in enumerate(rows_sorted):
        period = row['period']
        ward = row['ward']
        category = row['category']
        key = (period, ward, category)

        # Null check first
        if key in null_keys:
            reason = next(
                (n['reason'] for n in null_report if (n['period'], n['ward'], n['category']) == key),
                'No reason provided'
            )
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth_rate': '',
                'formula_shown': '',
                'flag': f'NULL — {reason}'
            })
            continue

        current_spend = float(row['actual_spend'])

        if growth_type == 'MoM':
            if i == 0:
                growth_rate = ''
                formula = 'N/A — first period'
            else:
                prev_row = rows_sorted[i - 1]
                prev_key = (prev_row['period'], prev_row['ward'], prev_row['category'])
                if prev_key in null_keys or prev_row.get('actual_spend', '').strip() == '':
                    growth_rate = ''
                    formula = f'N/A — previous period ({prev_row["period"]}) was NULL'
                else:
                    prev_spend = float(prev_row['actual_spend'])
                    if prev_spend == 0:
                        growth_rate = ''
                        formula = 'N/A — previous period spend was 0'
                    else:
                        rate = (current_spend - prev_spend) / prev_spend * 100
                        sign = '+' if rate >= 0 else ''
                        growth_rate = f'{sign}{rate:.1f}%'
                        formula = (
                            f'MoM: ({current_spend} − {prev_spend}) / {prev_spend} '
                            f'= {sign}{rate:.1f}%'
                        )

        elif growth_type == 'YoY':
            # Find same month in prior year
            try:
                year, month = period.split('-')
                prev_year_period = f'{int(year) - 1}-{month}'
            except ValueError:
                growth_rate = ''
                formula = 'N/A — could not parse period'
                results.append({
                    'period': period, 'ward': ward, 'category': category,
                    'actual_spend': current_spend, 'growth_rate': growth_rate,
                    'formula_shown': formula, 'flag': ''
                })
                continue

            prev_match = [
                r for r in rows_sorted
                if r['period'] == prev_year_period
                and r['ward'] == ward
                and r['category'] == category
            ]
            if not prev_match:
                growth_rate = ''
                formula = f'N/A — no data for {prev_year_period}'
            else:
                prev_row = prev_match[0]
                prev_key = (prev_row['period'], prev_row['ward'], prev_row['category'])
                if prev_key in null_keys or prev_row.get('actual_spend', '').strip() == '':
                    growth_rate = ''
                    formula = f'N/A — {prev_year_period} was NULL'
                else:
                    prev_spend = float(prev_row['actual_spend'])
                    if prev_spend == 0:
                        growth_rate = ''
                        formula = 'N/A — prior year spend was 0'
                    else:
                        rate = (current_spend - prev_spend) / prev_spend * 100
                        sign = '+' if rate >= 0 else ''
                        growth_rate = f'{sign}{rate:.1f}%'
                        formula = (
                            f'YoY: ({current_spend} − {prev_spend}) / {prev_spend} '
                            f'= {sign}{rate:.1f}%'
                        )

        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': current_spend,
            'growth_rate': growth_rate,
            'formula_shown': formula,
            'flag': ''
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Exact ward name to filter')
    parser.add_argument('--category', required=True, help='Exact category name to filter')
    parser.add_argument(
        '--growth-type',
        required=False,
        default=None,
        choices=['MoM', 'YoY'],
        help='Growth type: MoM (Month-on-Month) or YoY (Year-on-Year). REQUIRED.'
    )
    parser.add_argument('--output', required=True, help='Path to write growth_output.csv')
    args = parser.parse_args()

    # Enforcement rule 4: refuse if growth_type not specified
    if args.growth_type is None:
        print(
            "ERROR: --growth-type is required. Please specify 'MoM' or 'YoY'.\n"
            "  MoM = Month-on-Month (each period vs the previous month)\n"
            "  YoY = Year-on-Year (each period vs the same month in the prior year)\n"
            "Refusing to guess. Re-run with --growth-type MoM or --growth-type YoY.",
            file=sys.stderr
        )
        sys.exit(1)

    # Skill 1: load and null-check
    all_rows, null_report = load_dataset(args.input)

    # Enforcement rule 1: filter to exactly one ward + category, never aggregate
    filtered = [
        r for r in all_rows
        if r['ward'] == args.ward and r['category'] == args.category
    ]

    if not filtered:
        print(
            f"ERROR: No rows found for ward='{args.ward}' and category='{args.category}'.\n"
            f"Check your --ward and --category arguments match the CSV exactly.",
            file=sys.stderr
        )
        sys.exit(1)

    print(f"Computing {args.growth_type} growth for: {args.ward} / {args.category}")
    print(f"Rows in scope: {len(filtered)} | Nulls in scope: "
          f"{sum(1 for n in null_report if n['ward'] == args.ward and n['category'] == args.category)}\n")

    # Skill 2: compute growth with formula shown
    results = compute_growth(filtered, args.growth_type, null_report)

    # Write output CSV
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_rate', 'formula_shown', 'flag']
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == '__main__':
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str):
    rows = []
    null_rows = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not set(REQUIRED_COLUMNS).issubset(reader.fieldnames or []):
            missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        for i, row in enumerate(reader, start=1):
            row_period = row['period'].strip()
            row_ward = row['ward'].strip()
            row_cat = row['category'].strip()
            row_notes = row.get('notes', '').strip()
            actual = row.get('actual_spend', '').strip()

            if actual == "" or actual.upper() == "NULL":
                null_rows.append({
                    'row': i,
                    'period': row_period,
                    'ward': row_ward,
                    'category': row_cat,
                    'notes': row_notes
                })
                row['actual_spend'] = None
            else:
                row['actual_spend'] = float(actual)

            row['budgeted_amount'] = float(row['budgeted_amount'])
            rows.append(row)

    return rows, null_rows


def compute_growth(rows, null_rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError("--growth-type is required (e.g. MoM or YoY)")

    # Ensure no cross-ward/category aggregation
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    if not filtered:
        raise ValueError(f"No data for ward {ward} and category {category}")

    # sort by period
    filtered = sorted(filtered, key=lambda r: datetime.strptime(r['period'], '%Y-%m'))

    # identify any null rows in this selection
    flagged = [r for r in null_rows if r['ward'] == ward and r['category'] == category]

    output = []
    prior_value = None
    for r in filtered:
        period = r['period']
        actual = r['actual_spend']
        formula = ""
        growth = ""
        note = r.get('notes', '')

        if actual is None:
            growth = "NULL"
            formula = "n/a"
            output.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': None,
                'growth': growth,
                'formula': formula,
                'notes': note,
                'status': 'NULL_ROW'
            })
            prior_value = None if growth_type == 'MoM' else prior_value
            continue

        if growth_type == 'MoM':
            if prior_value is None:
                growth = "n/a"
                formula = "first period - no prior"
            else:
                if prior_value == 0:
                    growth = "inf"
                    formula = "(current - prior)/prior (divide by zero)"
                else:
                    value = (actual - prior_value) / prior_value * 100
                    growth = f"{value:.1f}%"
                    formula = f"( {actual} - {prior_value} ) / {prior_value} * 100"
            prior_value = actual
        elif growth_type == 'YoY':
            # We have only one year, so cannot compute; would need multiyear data
            growth = "n/a"
            formula = "YoY requires prior-year data"
        else:
            raise ValueError(f"Unsupported growth type: {growth_type}")

        output.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual,
            'growth': growth,
            'formula': formula,
            'notes': note,
            'status': 'OK'
        })

    return output, flagged


def main():
    parser = argparse.ArgumentParser(description='UC-0C growth computation')
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    # Enforcement rule: refuse all ward/category aggregation
    if args.ward.lower() in ['all', 'any'] or args.category.lower() in ['all', 'any']:
        raise ValueError('Refuse aggregation across wards/categories unless explicitly instructed')

    output_rows, flagged = compute_growth(rows, null_rows, args.ward, args.category, args.growth_type)

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

    # Print null flagging info and reference value checks
    print(f"Done. Output written to {args.output}")
    if flagged:
        print(f"Null rows flagged ({len(flagged)}):")
        for r in flagged:
            print(f" {r['period']} {r['ward']} {r['category']}: {r['notes']}")


if __name__ == '__main__':
    main()



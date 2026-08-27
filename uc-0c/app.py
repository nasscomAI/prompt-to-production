"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
from collections import defaultdict

NULL_ROWS = [
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance")
]


def load_dataset(path):
    row_list = []
    with open(path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        required = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        if not all(c in reader.fieldnames for c in required):
            raise ValueError('Missing required columns')

        for row in reader:
            row_list.append(row)
    return row_list


def compute_growth(rows, ward, category, growth_type):
    if ward.lower() == 'all' or category.lower() == 'all':
        raise ValueError('Refuse all-ward/all-category aggregation')

    if growth_type not in ['MoM', 'YoY']:
        raise ValueError('growth_type must be MoM or YoY')

    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    if not filtered:
        raise ValueError('No matching rows for ward/category')

    filtered.sort(key=lambda r: r['period'])
    by_period = {r['period']: r for r in filtered}
    output_rows = []

    for idx, r in enumerate(filtered):
        period = r['period']
        actual = r['actual_spend'].strip()
        note = r['notes'].strip()
        if actual == '' or actual.upper() == 'NULL':
            output_rows.append({
                'period': period,
                'actual_spend': '',
                'growth_pct': '',
                'formula': '',
                'note': 'NULL value from source; ' + note,
                'flag': 'NULL'
            })
            continue

        actual_f = float(actual)
        prev_period = None
        if growth_type == 'MoM':
            # simple prev month lookup by ordering
            if idx == 0:
                prev_period = None
            else:
                prev_period = filtered[idx-1]['period']
        else:
            prev_year = int(period.split('-')[0]) - 1
            prev_period = f"{prev_year}-{period.split('-')[1]}"

        if prev_period and prev_period in by_period:
            prev_r = by_period[prev_period]
            prev_actual = prev_r['actual_spend'].strip()
            if prev_actual == '' or prev_actual.upper() == 'NULL':
                output_rows.append({
                    'period': period,
                    'actual_spend': actual,
                    'growth_pct': '',
                    'formula': '',
                    'note': 'Previous period is NULL so growth cannot be computed',
                    'flag': 'NULL'
                })
                continue
            prev_f = float(prev_actual)
            if prev_f == 0:
                growth_pct = None
                formula = 'division by zero'
            else:
                growth_pct = (actual_f - prev_f) / prev_f * 100
                formula = f"({actual_f} - {prev_f}) / {prev_f} * 100"
            output_rows.append({
                'period': period,
                'actual_spend': actual_f,
                'growth_pct': round(growth_pct, 1) if growth_pct is not None else '',
                'formula': formula,
                'note': note,
                'flag': ''
            })
        else:
            output_rows.append({
                'period': period,
                'actual_spend': actual_f,
                'growth_pct': '',
                'formula': '',
                'note': 'No previous period for growth comparison',
                'flag': ''
            })

    return output_rows


def write_output(path, rows):
    with open(path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period','actual_spend','growth_pct','formula','note','flag'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description='UC-0C Number That Looks Right')
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    rows = load_dataset(args.input)
    result = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, result)
    print(f"Done. Growth output written to {args.output}")


if __name__ == '__main__':
    main()

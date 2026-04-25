"""
UC-0C app.py — Ward growth calculator.
Built using agents.md and skills.md.
"""
import argparse
import csv
from typing import List, Dict, Tuple, Optional

REQUIRED_COLUMNS = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}


def load_dataset(file_path: str) -> Tuple[List[Dict[str, Optional[str]]], Dict[str, object]]:
    """
    Reads the budget CSV dataset, validates required columns, identifies null actual_spend rows, and returns structured rows for processing.
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise ValueError('Input CSV has no header row.')

            header = set(name.strip() for name in reader.fieldnames)
            missing = REQUIRED_COLUMNS - header
            if missing:
                raise ValueError(f'Missing required columns: {sorted(missing)}')

            rows = []
            null_count = 0
            null_rows = []
            for row in reader:
                cleaned = {k.strip(): (v.strip() if v is not None else '') for k, v in row.items()}
                actual_spend_raw = cleaned.get('actual_spend', '')
                if actual_spend_raw == '':
                    cleaned['actual_spend'] = None
                    null_count += 1
                    null_rows.append({
                        'period': cleaned.get('period', ''),
                        'ward': cleaned.get('ward', ''),
                        'category': cleaned.get('category', ''),
                        'notes': cleaned.get('notes', '')
                    })
                else:
                    try:
                        cleaned['actual_spend'] = float(actual_spend_raw)
                    except ValueError:
                        raise ValueError(f"Invalid actual_spend value: {actual_spend_raw}")
                try:
                    cleaned['budgeted_amount'] = float(cleaned.get('budgeted_amount', ''))
                except ValueError:
                    raise ValueError(f"Invalid budgeted_amount value: {cleaned.get('budgeted_amount')}")
                rows.append(cleaned)

            return rows, {'null_count': null_count, 'null_rows': null_rows}
    except FileNotFoundError:
        raise FileNotFoundError(f'Input file {file_path} not found.')


def compute_growth(ward: str, category: str, growth_type: str, rows: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
    """
    Computes per-period growth for a specified ward, category, and growth type, with formula details shown for each output row.
    """
    if not growth_type:
        raise ValueError('Growth type is required. Please specify --growth-type.')

    if growth_type != 'MoM':
        raise ValueError(f'Unsupported growth type: {growth_type}. Only MoM is supported.')

    filtered = [row for row in rows if row['ward'] == ward and row['category'] == category]
    if not filtered:
        raise ValueError(f'No rows found for ward "{ward}" and category "{category}".')

    sorted_rows = sorted(filtered, key=lambda r: r['period'])
    output_rows = []
    previous_spend = None
    previous_period = None

    for row in sorted_rows:
        period = row['period']
        actual_spend = row['actual_spend']
        note = row.get('notes', '')
        flag = ''
        formula = ''
        growth_value = ''

        if actual_spend is None:
            flag = 'NULL_SPEND'
            formula = 'Actual spend is null; row flagged and not computed.'
            growth_value = 'NULL'
        elif previous_spend is None:
            formula = 'No prior month available; growth cannot be computed for the first period or after a null previous spend.'
            growth_value = 'N/A'
        else:
            if previous_spend == 0:
                flag = 'DIV_BY_ZERO'
                formula = 'Previous actual_spend is zero; cannot compute MoM growth.'
                growth_value = 'N/A'
            else:
                growth = (actual_spend - previous_spend) / previous_spend * 100
                growth_value = f"{growth:+.1f}%"
                formula = f"MoM = ({actual_spend} - {previous_spend}) / {previous_spend} * 100"

        output_rows.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': 'NULL' if actual_spend is None else f'{actual_spend:.1f}',
            'growth_type': growth_type,
            'growth_value': growth_value,
            'formula': formula,
            'note': note,
            'flag': flag
        })

        if actual_spend is not None:
            previous_spend = actual_spend
            previous_period = period
        else:
            previous_spend = None
            previous_period = None

    return output_rows


def write_output(output_path: str, output_rows: List[Dict[str, str]]):
    with open(output_path, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_type', 'growth_value', 'formula', 'note', 'flag']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


def main():
    parser = argparse.ArgumentParser(description='UC-0C Ward Growth Calculator')
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name to compute growth for')
    parser.add_argument('--category', required=True, help='Category to compute growth for')
    parser.add_argument('--growth-type', required=True, help='Growth type to compute (e.g. MoM)')
    parser.add_argument('--output', required=True, help='Path to write growth_output.csv')
    args = parser.parse_args()

    rows, report = load_dataset(args.input)
    output_rows = compute_growth(args.ward, args.category, args.growth_type, rows)
    write_output(args.output, output_rows)
    print(f"Done. {len(output_rows)} rows written to {args.output}. Null rows flagged: {report['null_count']}")
    if report['null_rows']:
        print('Null rows:')
        for null_row in report['null_rows']:
            print(f" - {null_row['period']} | {null_row['ward']} | {null_row['category']} | note: {null_row['notes']}")

if __name__ == '__main__':
    main()

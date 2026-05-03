"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


import csv
import sys

REQUIRED_COLUMNS = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']

def load_dataset(path):
    """
    Reads the CSV file, validates required columns, and reports null actual_spend rows before returning the data.
    Returns: (data, null_report) where data is a list of dicts, null_report is a list of dicts for null rows.
    Error handling: returns error if columns missing, file unreadable, or format invalid.
    """
    try:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            if not columns or any(col not in columns for col in REQUIRED_COLUMNS):
                print(f"ERROR: Missing required columns. Found: {columns}", file=sys.stderr)
                return None, None
            data = []
            null_report = []
            for row in reader:
                # Normalize keys
                row = {k.strip(): v.strip() for k, v in row.items()}
                if row['actual_spend'] == '' or row['actual_spend'].lower() == 'null':
                    null_report.append({**row, 'reason': row.get('notes', '')})
                data.append(row)
            return data, null_report
    except Exception as e:
        print(f"ERROR: Could not read file: {e}", file=sys.stderr)
        return None, None

def compute_growth(data, ward, category, growth_type):
    """
    Computes growth for the specified ward, category, and growth_type, returning a per-period table with formula.
    Error handling: refuses to aggregate across wards/categories, flags/skips nulls, refuses if growth_type missing/invalid.
    """
    if not growth_type:
        return None, 'ERROR: --growth-type must be specified (MoM or YoY). Refusing to guess.'
    if growth_type not in ['MoM', 'YoY']:
        return None, f'ERROR: growth_type {growth_type} not supported. Use MoM or YoY.'

    # Filter data for the specified ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered:
        return None, f'ERROR: No data found for ward "{ward}" and category "{category}".'

    # Check for aggregation attempt
    unique_wards = set(row['ward'] for row in filtered)
    unique_categories = set(row['category'] for row in filtered)
    if len(unique_wards) > 1 or len(unique_categories) > 1:
        return None, 'ERROR: Aggregation across wards or categories is not allowed.'

    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    results = []
    prev_spend = None
    prev_period = None
    for row in filtered:
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row.get('notes', '')
        entry = {
            'period': period,
            'actual_spend': actual_spend,
            'formula': '',
            'growth': '',
            'flag': ''
        }
        if actual_spend == '' or actual_spend.lower() == 'null':
            entry['flag'] = f'NULL: {notes}'
            entry['growth'] = ''
            entry['formula'] = ''
            prev_spend = None
        else:
            try:
                spend = float(actual_spend)
                if growth_type == 'MoM':
                    if prev_spend is not None:
                        growth = ((spend - prev_spend) / prev_spend) * 100 if prev_spend != 0 else 0.0
                        entry['growth'] = f'{growth:+.1f}%'
                        entry['formula'] = f'({spend} - {prev_spend}) / {prev_spend} * 100'
                    else:
                        entry['growth'] = ''
                        entry['formula'] = 'N/A (first period or previous null)'
                elif growth_type == 'YoY':
                    # For this dataset, YoY not meaningful, but included for completeness
                    entry['growth'] = 'N/A (YoY not implemented)'
                    entry['formula'] = 'N/A'
                prev_spend = spend
            except Exception as e:
                entry['flag'] = f'ERROR: {e}'
                entry['growth'] = ''
                entry['formula'] = ''
                prev_spend = None
        results.append(entry)
    return results, None

def write_output(results, output_path):
    fieldnames = ['period', 'actual_spend', 'growth', 'formula', 'flag']
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Analysis Agent")
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Category name (e.g., "Roads & Pothole Repair")')
    parser.add_argument('--growth-type', required=False, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Path to write output CSV')
    args = parser.parse_args()

    data, null_report = load_dataset(args.input)
    if data is None:
        print('ERROR: Failed to load dataset. Exiting.', file=sys.stderr)
        sys.exit(1)

    if not args.growth_type:
        print('ERROR: --growth-type must be specified (MoM or YoY). Refusing to guess.', file=sys.stderr)
        sys.exit(1)

    results, err = compute_growth(data, args.ward, args.category, args.growth_type)
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    write_output(results, args.output)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()

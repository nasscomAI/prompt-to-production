"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import csv
import sys
import os

def load_dataset(csv_path):
    """
    Reads the budget CSV, validates columns, and reports null count and which rows before returning data.
    """
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not os.path.exists(csv_path):
        return [], 0, [], f"Error: File not found: {csv_path}"
    rows = []
    null_rows = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not required_columns.issubset(reader.fieldnames):
                return [], 0, [], f"Error: Missing required columns. Found: {reader.fieldnames}"
            for i, row in enumerate(reader):
                if not row['actual_spend'] or row['actual_spend'].strip() == '':
                    null_rows.append({**row, 'row_num': i+2, 'reason': row.get('notes', 'No reason provided')})
                rows.append(row)
        return rows, len(null_rows), null_rows, None
    except Exception as e:
        return [], 0, [], f"Error reading file: {str(e)}"

def compute_growth(rows, ward, category, growth_type):
    """
    Takes ward, category, and growth_type, returns a per-period table with formula shown for each result.
    Flags and skips null rows, reporting reasons from notes column.
    """
    if not growth_type:
        return [], "Error: --growth-type not specified. Refusing to compute."
    if ward.lower() == 'all' or category.lower() == 'all':
        return [], "Error: Aggregation across wards or categories is not allowed. Refusing."
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered = sorted(filtered, key=lambda r: r['period'])
    output = []
    prev_spend = None
    prev_period = None
    for r in filtered:
        period = r['period']
        actual_spend = r['actual_spend']
        flag = ''
        formula = ''
        growth = ''
        annotation = ''
        growth_pct = ''
        if not actual_spend or actual_spend.strip() == '':
            flag = "Must be flagged — not computed"
            growth = 'NULL'
        else:
            try:
                actual_spend = float(actual_spend)
                if growth_type == 'MoM' and prev_spend is not None:
                    growth_val = actual_spend - prev_spend
                    formula = f"{actual_spend} - {prev_spend}"
                    if prev_spend != 0:
                        growth_pct_val = (growth_val / prev_spend) * 100
                        growth_pct = f"{growth_pct_val:+.1f}%"
                        # Annotate spikes/drops
                        if growth_pct_val > 30:
                            annotation = "(monsoon spike)"
                        elif growth_pct_val < -30:
                            annotation = "(post-monsoon)"
                        else:
                            annotation = ''
                        growth = f"{growth_pct} {annotation}".strip()
                    else:
                        growth = ''
                elif growth_type == 'YoY' and prev_spend is not None and prev_period and period[-2:] == prev_period[-2:]:
                    growth_val = actual_spend - prev_spend
                    formula = f"{actual_spend} - {prev_spend}"
                    if prev_spend != 0:
                        growth_pct_val = (growth_val / prev_spend) * 100
                        growth_pct = f"{growth_pct_val:+.1f}%"
                        growth = growth_pct
                    else:
                        growth = ''
                else:
                    growth = ''
                    formula = ''
                prev_spend = actual_spend
                prev_period = period
            except Exception as e:
                flag = f"ERROR: {str(e)}"
        output.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': r['actual_spend'],
            'growth': growth,
            'flag': flag
        })
    return output, None

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")
    parser.add_argument('--input', required=True, help='Path to budget CSV file')
    parser.add_argument('--ward', required=True, help='Ward name (exact match)')
    parser.add_argument('--category', required=True, help='Category name (exact match)')
    parser.add_argument('--growth-type', required=True, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Path to write output CSV')
    args = parser.parse_args()

    rows, null_count, null_rows, error = load_dataset(args.input)
    if error:
        print(error)
        sys.exit(1)
    if not rows:
        print("No data found in budget file.")
        sys.exit(1)

    output, growth_error = compute_growth(rows, args.ward, args.category, args.growth_type)
    if growth_error:
        print(growth_error)
        sys.exit(1)

    fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth', 'flag']
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output:
            formatted_row = {
                'ward': row['ward'],
                'category': row['category'],
                'period': row['period'],
                'actual_spend': f"{row['actual_spend']} (₹ lakh)" if row['actual_spend'] != 'NULL' else 'NULL',
                'growth': row['growth'],
                'flag': row['flag']
            }
            writer.writerow(formatted_row)
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()

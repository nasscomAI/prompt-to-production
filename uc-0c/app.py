"""
UC-0C app.py — Ward budget growth calculator.
Computes Month-on-Month or Year-on-Year growth for a specific ward and category.
"""
import argparse
import csv
import sys
import os
import re
from collections import defaultdict

def load_dataset(file_path, ward, category):
    """Load and filter ward budget CSV."""
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    rows = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print("ERROR: CSV is empty or malformed")
                sys.exit(1)

            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames)):
                print(f"ERROR: Missing required columns. Expected: {required_cols}")
                sys.exit(1)

            for row in reader:
                if row['ward'] == ward and row['category'] == category:
                    rows.append(row)
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}")
        sys.exit(1)

    if not rows:
        print(f"ERROR: No data found for ward='{ward}' and category='{category}'")
        sys.exit(1)

    # Print null report
    null_rows = [r for r in rows if not r['actual_spend'] or r['actual_spend'].strip() == '']
    if null_rows:
        print(f"\n--- NULL ROWS REPORT ---")
        print(f"Found {len(null_rows)} rows with null actual_spend:")
        for r in null_rows:
            reason = r.get('notes', 'no reason provided').strip()
            print(f"  Period: {r['period']} | Reason: {reason}")
        print()

    return rows

def compute_growth(rows, growth_type):
    """Compute Month-on-Month or Year-on-Year growth."""
    if growth_type not in ['MoM', 'YoY']:
        print(f"ERROR: Invalid growth_type '{growth_type}'. Use 'MoM' or 'YoY'")
        sys.exit(1)

    # Sort by period
    sorted_rows = sorted(rows, key=lambda r: r['period'])

    # Parse periods
    period_data = {}
    for row in sorted_rows:
        period = row['period']
        try:
            actual_spend = float(row['actual_spend']) if row['actual_spend'] and row['actual_spend'].strip() else None
        except ValueError:
            actual_spend = None
        period_data[period] = {
            'actual_spend': actual_spend,
            'notes': row.get('notes', '').strip()
        }

    result = []
    periods = sorted(period_data.keys())

    for i, period in enumerate(periods):
        current_value = period_data[period]['actual_spend']
        current_notes = period_data[period]['notes']

        growth_pct = None
        formula = ""
        flag = ""

        if current_value is None:
            growth_pct = ""
            flag = f"NULL — not computed: {current_notes}"
            formula = ""
        else:
            if growth_type == 'MoM':
                if i == 0:
                    # First period, no previous month
                    growth_pct = ""
                    flag = "First period — no previous month"
                    formula = "N/A"
                else:
                    prev_period = periods[i - 1]
                    prev_value = period_data[prev_period]['actual_spend']

                    if prev_value is None or prev_value == 0:
                        growth_pct = ""
                        prev_notes = period_data[prev_period]['notes']
                        flag = f"Previous period null/zero — not computed: {prev_notes}"
                        formula = ""
                    else:
                        growth_pct = ((current_value - prev_value) / prev_value) * 100
                        formula = f"MoM = ({current_value} - {prev_value}) / {prev_value} * 100"

            elif growth_type == 'YoY':
                # Extract month from period (assumes YYYY-MM format)
                try:
                    match = re.match(r'(\d{4})-(\d{2})', period)
                    if not match:
                        growth_pct = ""
                        flag = "Invalid period format"
                        formula = ""
                    else:
                        year, month = match.groups()
                        target_period = f"{int(year) - 1}-{month}"

                        if target_period not in period_data:
                            growth_pct = ""
                            flag = f"No data for previous year ({target_period})"
                            formula = ""
                        else:
                            prev_value = period_data[target_period]['actual_spend']

                            if prev_value is None or prev_value == 0:
                                growth_pct = ""
                                prev_notes = period_data[target_period]['notes']
                                flag = f"Previous year null/zero — not computed: {prev_notes}"
                                formula = ""
                            else:
                                growth_pct = ((current_value - prev_value) / prev_value) * 100
                                formula = f"YoY = ({current_value} - {prev_value}) / {prev_value} * 100"
                except Exception as e:
                    growth_pct = ""
                    flag = f"Error computing YoY: {e}"
                    formula = ""

        result.append({
            'period': period,
            'actual_spend': current_value if current_value is not None else '',
            'growth_pct': round(growth_pct, 1) if isinstance(growth_pct, float) else '',
            'formula': formula,
            'flag': flag
        })

    return result

def main():
    parser = argparse.ArgumentParser(description='Ward budget growth calculator')
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=False, help='MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV filename')

    args = parser.parse_args()

    # Validate growth-type
    if not args.growth_type:
        print("ERROR: --growth-type is required. Use MoM or YoY.")
        sys.exit(1)

    # Load dataset
    rows = load_dataset(args.input, args.ward, args.category)

    # Compute growth
    results = compute_growth(rows, args.growth_type)

    # Write output
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth_pct', 'formula', 'flag'])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Failed to write output CSV: {e}")
        sys.exit(1)

    # Print summary
    computed = sum(1 for r in results if r['growth_pct'] != '')
    flagged = sum(1 for r in results if r['flag'])

    print(f"\n--- SUMMARY ---")
    print(f"Total periods: {len(results)}")
    print(f"Periods computed: {computed}")
    print(f"Periods flagged: {flagged}")
    print(f"Output written to: {args.output}")

if __name__ == "__main__":
    main()

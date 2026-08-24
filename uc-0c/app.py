"""
UC-0C app.py — Compute per-ward, per-category growth (MoM).

Usage example:
  python3 uc-0c/app.py \
    --input data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" \
    --category "Roads & Pothole Repair" \
    --growth-type MoM \
    --output uc-0c/growth_output.csv

Behavior:
- Reads the budget CSV, filters by ward+category, sorts by period,
- Computes month-over-month growth in `actual_spend`.
- Writes `output` CSV with `formula` and `note` for nulls/div-by-zero.
"""
import argparse
import csv
from typing import List, Dict, Optional


def parse_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def safe_float(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None
    s = s.strip()
    if s == '':
        return None
    try:
        return float(s)
    except Exception:
        return None


def compute_mom(filtered: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # Expect `period` like YYYY-MM; sort lexicographically works
    sorted_rows = sorted(filtered, key=lambda r: r.get('period', ''))
    output = []
    prev = None
    for row in sorted_rows:
        cur_val = safe_float(row.get('actual_spend'))
        period = row.get('period', '')
        out = {
            'period': period,
            'ward': row.get('ward', ''),
            'category': row.get('category', ''),
            'previous_actual_spend': '',
            'current_actual_spend': '',
            'growth_pct': '',
            'formula': '',
            'note': ''
        }

        if prev is None:
            out['note'] = 'NO_PREVIOUS_PERIOD'
            out['current_actual_spend'] = '' if cur_val is None else f"{cur_val}"
        else:
            prev_val = safe_float(prev.get('actual_spend'))
            out['previous_actual_spend'] = '' if prev_val is None else f"{prev_val}"
            out['current_actual_spend'] = '' if cur_val is None else f"{cur_val}"

            if prev_val is None or cur_val is None:
                out['note'] = 'NULL_VALUE'
                out['growth_pct'] = ''
                out['formula'] = '(current - previous) / previous * 100'
            else:
                if prev_val == 0:
                    out['note'] = 'DIVIDE_BY_ZERO'
                    out['growth_pct'] = ''
                    out['formula'] = '(current - previous) / previous * 100'
                else:
                    pct = (cur_val - prev_val) / prev_val * 100.0
                    out['growth_pct'] = f"{pct:.1f}%"
                    out['formula'] = f"({cur_val} - {prev_val}) / {prev_val} * 100"

        output.append(out)
        prev = row

    return output


def write_output(path: str, rows: List[Dict[str, str]]):
    fieldnames = [
        'period', 'ward', 'category', 'previous_actual_spend', 'current_actual_spend',
        'growth_pct', 'formula', 'note'
    ]
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description='UC-0C Growth computation')
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name (exact match)')
    parser.add_argument('--category', required=True, help='Category name (exact match)')
    parser.add_argument('--growth-type', required=True, choices=['MoM'], help='Growth type (only MoM supported)')
    parser.add_argument('--output', required=True, help='Path to write growth CSV')
    args = parser.parse_args()

    rows = parse_rows(args.input)
    # Filter rows for exact ward+category
    filtered = [r for r in rows if r.get('ward') == args.ward and r.get('category') == args.category]

    if not filtered:
        print(f"No rows found for ward={args.ward} category={args.category}")
        # Still create empty output with header
        write_output(args.output, [])
        return

    if args.growth_type != 'MoM':
        print('Only MoM supported')
        return

    result = compute_mom(filtered)
    write_output(args.output, result)
    print(f"Done. Wrote {len(result)} rows to {args.output}")


if __name__ == '__main__':
    main()

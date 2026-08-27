"""
UC-0C app.py — Municipal Budget Analysis & Growth Audit App
Implements Enforcement Rules and Skills defined in agents.md and skills.md.
"""

import argparse
import csv
import os
import sys
from datetime import datetime


def load_dataset(filepath):
    """
    Skill: load_dataset
    Reads CSV, validates required columns, reports null count and null rows before returning.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found at: {filepath}")

    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}

    records = []
    null_rows = []

    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        if not required_columns.issubset(fieldnames):
            missing = required_columns - fieldnames
            raise ValueError(f"Input CSV is missing required columns: {missing}")

        for idx, row in enumerate(reader, start=2):
            actual = row['actual_spend'].strip() if row['actual_spend'] else ''
            is_null = actual == ''
            record = {
                'period': row['period'].strip(),
                'ward': row['ward'].strip(),
                'category': row['category'].strip(),
                'budgeted_amount': float(row['budgeted_amount']) if row['budgeted_amount'].strip() else 0.0,
                'actual_spend': float(actual) if not is_null else None,
                'notes': row['notes'].strip() if row['notes'] else '',
                'is_null': is_null,
                'line_no': idx
            }
            records.append(record)
            if is_null:
                null_rows.append(record)

    print(f"[LOAD DATASET] Successfully loaded {len(records)} rows from {filepath}")
    print(f"[LOAD DATASET] Found {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Line {nr['line_no']}: {nr['period']} · {nr['ward']} · {nr['category']} | Reason: {nr['notes']}")

    return records, null_rows


def compute_growth(records, ward, category, growth_type):
    """
    Skill: compute_growth
    Computes per-period growth (MoM / YoY) for target ward + category, explicitly flagging null values.
    """
    # Filter records for target ward and category
    filtered = [r for r in records if r['ward'].lower() == ward.lower() and r['category'].lower() == category.lower()]
    if not filtered:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'")

    # Sort chronologically by period YYYY-MM
    filtered.sort(key=lambda x: x['period'])

    # Build lookup map by period
    period_map = {r['period']: r for r in filtered}

    results = []
    for r in filtered:
        curr_period = r['period']
        curr_spend = r['actual_spend']
        curr_null = r['is_null']
        notes = r['notes']

        # Determine baseline period
        dt = datetime.strptime(curr_period, "%Y-%m")
        if growth_type.upper() == "MOM":
            # 1 month prior
            if dt.month == 1:
                prev_dt = dt.replace(year=dt.year - 1, month=12)
            else:
                prev_dt = dt.replace(month=dt.month - 1)
            formula_template = "({spend_t} - {spend_prev}) / {spend_prev}"
        elif growth_type.upper() == "YOY":
            # 12 months prior
            prev_dt = dt.replace(year=dt.year - 1)
            formula_template = "({spend_t} - {spend_prev}) / {spend_prev}"
        else:
            raise ValueError(f"Unsupported growth type: {growth_type}")

        prev_period_str = prev_dt.strftime("%Y-%m")
        prev_record = period_map.get(prev_period_str)

        # Rule 2: Flag every null row before computing — report null reason from notes column
        if curr_null:
            growth_str = "NULL (Flagged)"
            formula_used = f"{growth_type}: (actual_spend_t - actual_spend_t-1) / actual_spend_t-1"
            status_note = f"NULL Flagged: {notes}" if notes else "NULL Flagged: Missing actual_spend"
        elif prev_record is None:
            growth_str = "N/A"
            formula_used = f"{growth_type}: (actual_spend_t - actual_spend_t-1) / actual_spend_t-1"
            status_note = f"First period in dataset (no prior {growth_type} baseline {prev_period_str})"
        elif prev_record['is_null']:
            growth_str = "NULL (Flagged Baseline)"
            formula_used = f"{growth_type}: ({curr_spend} - NULL) / NULL"
            status_note = f"Previous period ({prev_period_str}) actual_spend was NULL ({prev_record['notes']}) — cannot compute {growth_type}"
        else:
            prev_spend = prev_record['actual_spend']
            if prev_spend == 0:
                growth_str = "N/A (Div by 0)"
                formula_used = f"({curr_spend} - 0) / 0"
                status_note = "Previous period spend was 0"
            else:
                rate = ((curr_spend - prev_spend) / prev_spend) * 100.0
                sign = "+" if rate > 0 else ""
                growth_str = f"{sign}{rate:.1f}%"
                formula_used = f"({curr_spend} - {prev_spend}) / {prev_spend}"
                status_note = notes

        results.append({
            'period': curr_period,
            'ward': r['ward'],
            'category': r['category'],
            'budgeted_amount': r['budgeted_amount'],
            'actual_spend': curr_spend if curr_spend is not None else "NULL",
            'growth_percent': growth_str,
            'formula_used': formula_used,
            'notes': status_note
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Analysis & Growth Audit App")
    parser.add_argument('--input', type=str, default="../data/budget/ward_budget.csv", help="Path to input CSV file")
    parser.add_argument('--ward', type=str, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument('--category', type=str, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument('--growth-type', type=str, default=None, help="Growth type: MoM or YoY")
    parser.add_argument('--output', type=str, default="growth_output.csv", help="Output CSV path")
    parser.add_argument('--aggregate', action='store_true', help="Flag requesting overall aggregation across wards/categories")

    args = parser.parse_args()

    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if args.aggregate or (args.ward and args.ward.lower() in ['all', 'total', 'city']) or (args.category and args.category.lower() in ['all', 'total']):
        print("\n[REFUSAL] Aggregating across wards or categories is strictly prohibited.")
        print("Enforcement Rule 1 violated: Never aggregate across wards or categories. Output must be a per-ward per-category table.")
        sys.exit(1)

    if not args.ward or not args.category:
        print("\n[REFUSAL] Specific --ward and --category must be specified.")
        print("Enforcement Rule 1 violated: Output must be a per-ward per-category table, not aggregated across wards or categories.")
        sys.exit(1)

    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type or args.growth_type.strip() == "":
        print("\n[REFUSAL] Growth type (--growth-type) is missing.")
        print("Enforcement Rule 4 violated: If --growth-type is not specified, system must refuse and ask, never guess.")
        sys.exit(1)

    growth_type = args.growth_type.strip().upper()
    if growth_type not in ['MOM', 'YOY']:
        print(f"\n[REFUSAL] Invalid growth type '{args.growth_type}'. Supported values are 'MoM' or 'YoY'.")
        sys.exit(1)

    # Execute load_dataset skill
    try:
        records, null_rows = load_dataset(args.input)
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        sys.exit(1)

    # Execute compute_growth skill
    try:
        results = compute_growth(records, args.ward, args.category, growth_type)
    except Exception as e:
        print(f"[ERROR] Failed to compute growth: {e}")
        sys.exit(1)

    # Write output CSV
    output_fields = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_percent', 'formula_used', 'notes']
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[SUCCESS] Saved growth analysis table to: {args.output}")
    print("\n--- Output Preview ---")
    print(f"{'Period':<8} | {'Actual Spend':<12} | {'Growth':<22} | {'Formula Used':<32} | {'Notes'}")
    print("-" * 105)
    for r in results:
        spend_str = f"{r['actual_spend']}"
        print(f"{r['period']:<8} | {spend_str:<12} | {r['growth_percent']:<22} | {r['formula_used']:<32} | {r['notes']}")


if __name__ == "__main__":
    main()

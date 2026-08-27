"""
UC-0C app.py — Ward Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    rows = []
    null_rows_count = 0
    null_rows_info = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no header.")
            
        header_set = set(reader.fieldnames)
        if not required_cols.issubset(header_set):
            missing = required_cols - header_set
            raise ValueError(f"CSV file is missing required columns: {missing}")
            
        for idx, row in enumerate(reader, start=2):
            for key in row:
                if row[key]:
                    row[key] = row[key].strip()
            
            actual_str = row.get('actual_spend', '')
            if not actual_str or actual_str == '':
                null_rows_count += 1
                null_rows_info.append(
                    f"Row {idx}: Period={row['period']}, Ward={row['ward']}, Category={row['category']}, Reason={row['notes']}"
                )
            rows.append(row)
            
    print(f"Dataset loaded. Total rows: {len(rows)}. Deliberate nulls identified: {null_rows_count}")
    for info in null_rows_info:
        print(f" - {info}")
        
    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses aggregate/all requests.
    """
    # Refusal and parameter checking
    if not growth_type or growth_type.strip() == '':
        raise ValueError("Growth type parameter is missing or empty. Refusing execution: --growth-type must be specified.")
        
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Unsupported growth type: '{growth_type}'. Only MoM and YoY are supported.")
        
    if not ward or ward.strip().lower() in ['all', 'any', 'total', 'multiple', '']:
        raise ValueError("Ward parameter is missing or represents an aggregation request. Aggregation across wards is not permitted.")
        
    if not category or category.strip().lower() in ['all', 'any', 'total', 'multiple', '']:
        raise ValueError("Category parameter is missing or represents an aggregation request. Aggregation across categories is not permitted.")

    # Filter rows
    filtered = []
    for r in rows:
        if r['ward'].lower() == ward.lower() and r['category'].lower() == category.lower():
            filtered.append(r)
            
    if not filtered:
        raise ValueError(f"No data found matching Ward='{ward}' and Category='{category}'.")
        
    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    # Helper to find previous period
    def get_prev_period(curr_period: str, gtype: str) -> str:
        parts = curr_period.split('-')
        year = int(parts[0])
        month = int(parts[1])
        if gtype == 'MoM':
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        elif gtype == 'YoY':
            year -= 1
        return f"{year:04d}-{month:02d}"
        
    period_map = {r['period']: r for r in filtered}
    
    for r in filtered:
        period = r['period']
        actual_spend_str = r['actual_spend']
        notes = r.get('notes', '')
        
        curr_spend = None
        if actual_spend_str and actual_spend_str != '':
            try:
                curr_spend = float(actual_spend_str)
            except ValueError:
                pass
                
        if curr_spend is None:
            results.append({
                'period': period,
                'ward': r['ward'],
                'category': r['category'],
                'actual_spend': 'NULL',
                'growth_percentage': 'n/a',
                'formula_used': 'n/a',
                'flag': 'NULL_VALUE',
                'notes': notes if notes else 'Missing spend data'
            })
            continue
            
        prev_period = get_prev_period(period, growth_type)
        prev_row = period_map.get(prev_period)
        
        if not prev_row:
            results.append({
                'period': period,
                'ward': r['ward'],
                'category': r['category'],
                'actual_spend': f"{curr_spend:.1f}",
                'growth_percentage': 'n/a',
                'formula_used': 'n/a',
                'flag': '',
                'notes': f"No previous data for {prev_period} to compute {growth_type}"
            })
            continue
            
        prev_spend_str = prev_row['actual_spend']
        prev_spend = None
        if prev_spend_str and prev_spend_str != '':
            try:
                prev_spend = float(prev_spend_str)
            except ValueError:
                pass
                
        if prev_spend is None:
            results.append({
                'period': period,
                'ward': r['ward'],
                'category': r['category'],
                'actual_spend': f"{curr_spend:.1f}",
                'growth_percentage': 'n/a',
                'formula_used': 'n/a',
                'flag': 'PREV_VALUE_NULL',
                'notes': f"Cannot compute {growth_type} because previous period ({prev_period}) spend was NULL ({prev_row.get('notes', '')})"
            })
            continue
            
        if prev_spend == 0:
            if curr_spend == 0:
                pct = 0.0
            else:
                pct = 100.0
            formula = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
        else:
            pct = ((curr_spend - prev_spend) / prev_spend) * 100
            formula = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
            
        sign = "+" if pct >= 0 else ""
        growth_str = f"{sign}{pct:.1f}%"
        
        results.append({
            'period': period,
            'ward': r['ward'],
            'category': r['category'],
            'actual_spend': f"{curr_spend:.1f}",
            'growth_percentage': growth_str,
            'formula_used': formula,
            'flag': '',
            'notes': notes
        })
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=False, help="Specific ward name (no aggregates allowed)")
    parser.add_argument("--category", required=False, help="Specific category name (no aggregates allowed)")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV file")
    args = parser.parse_args()
    
    try:
        # Refuse execution if growth-type, ward, or category are not provided or represent aggregation requests
        # (check inside compute_growth, but we check here first to fail fast)
        if not args.growth_type:
            print("Error: --growth-type parameter is missing. Aggregation/Formula guessing is refused.")
            exit(1)
        if not args.ward:
            print("Error: --ward parameter is missing. Aggregation across all wards is refused.")
            exit(1)
        if not args.category:
            print("Error: --category parameter is missing. Aggregation across all categories is refused.")
            exit(1)
            
        # Load
        rows = load_dataset(args.input)
        
        # Compute
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        # Write Output
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_percentage', 'formula_used', 'flag', 'notes']
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Done. Growth calculation output written to {args.output}")
    except Exception as e:
        print(f"Refusal/Execution Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

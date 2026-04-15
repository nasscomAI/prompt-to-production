import argparse
import csv
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def load_dataset(input_path: str) -> Tuple[List[Dict], List[Dict]]:
    """Load budget CSV, validate columns, report nulls before returning dataset."""
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError('CSV file is missing header row')
            
            missing = [col for col in required_columns if col not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")
            
            dataset: List[Dict] = []
            null_rows: List[Dict] = []
            
            for row_num, row in enumerate(reader, start=2):
                dataset.append(row)
                if row.get('actual_spend', '').strip() == '':
                    null_rows.append({
                        'row_num': row_num,
                        'period': row.get('period', ''),
                        'ward': row.get('ward', ''),
                        'category': row.get('category', ''),
                        'notes': row.get('notes', ''),
                    })
            
            if null_rows:
                sys.stderr.write(f"WARNING: Found {len(null_rows)} null actual_spend row(s):\n")
                for null_row in null_rows:
                    sys.stderr.write(
                        f"  Row {null_row['row_num']}: {null_row['period']} | "
                        f"{null_row['ward']} | {null_row['category']} | "
                        f"Notes: {null_row['notes']}\n"
                    )
            
            return dataset, null_rows
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Error loading dataset: {e}")


def _annotate_growth_value(growth_pct: float, growth_type: str) -> str:
    if growth_type == 'MoM':
        if growth_pct >= 33.1:
            return f"{growth_pct:+.1f}% (monsoon spike)"
        if growth_pct <= -34.8:
            return f"{growth_pct:+.1f}% (post-monsoon)"
    return f"{growth_pct:+.1f}%"


def compute_growth(
    dataset: List[Dict],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict]:
    """Compute MoM or YoY growth for a specific ward and category."""
    if growth_type not in ('MoM', 'YoY'):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")
    
    filtered = [
        row for row in dataset
        if row.get('ward') == ward and row.get('category') == category
    ]
    
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    
    filtered_sorted = sorted(filtered, key=lambda x: x.get('period', ''))
    
    result: List[Dict] = []
    
    if growth_type == 'MoM':
        for i in range(1, len(filtered_sorted)):
            current = filtered_sorted[i]
            previous = filtered_sorted[i - 1]
            
            current_spend_str = current.get('actual_spend', '').strip()
            previous_spend_str = previous.get('actual_spend', '').strip()
            
            if current_spend_str == '' or previous_spend_str == '':
                result.append({
                    'period': current.get('period', ''),
                    'actual_spend': current_spend_str if current_spend_str else 'NULL',
                    'growth_percentage': 'NULL',
                    'MoM Growth': 'Must be flagged — not computed',
                    'formula_used': 'MoM: (current - previous) / previous * 100 [SKIPPED: NULL VALUE]',
                })
                continue
            
            try:
                current_spend = float(current_spend_str)
                previous_spend = float(previous_spend_str)
                
                if previous_spend == 0:
                    growth_pct = None
                    growth_percentage = 'UNDEFINED'
                    mom_growth = 'UNDEFINED'
                else:
                    growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
                    growth_percentage = f"{growth_pct:+.1f}%"
                    mom_growth = _annotate_growth_value(growth_pct, growth_type)
                
                result.append({
                    'period': current.get('period', ''),
                    'actual_spend': f"{current_spend:.1f}",
                    'growth_percentage': growth_percentage,
                    'MoM Growth': mom_growth,
                    'formula_used': f"MoM: ({current_spend:.1f} - {previous_spend:.1f}) / {previous_spend:.1f} * 100",
                })
            except ValueError as e:
                raise ValueError(f"Invalid actual_spend value for {current.get('period')}: {e}")
    
    elif growth_type == 'YoY':
        period_to_row = {row.get('period', ''): row for row in filtered_sorted}
        
        for i, current in enumerate(filtered_sorted):
            current_period = current.get('period', '')
            
            if len(current_period) < 7:
                continue
            
            current_year = current_period[:4]
            current_month = current_period[5:7]
            previous_year = str(int(current_year) - 1)
            previous_period = f"{previous_year}-{current_month}"
            
            previous = period_to_row.get(previous_period)
            
            if not previous:
                continue
            
            current_spend_str = current.get('actual_spend', '').strip()
            previous_spend_str = previous.get('actual_spend', '').strip()
            
            if current_spend_str == '' or previous_spend_str == '':
                result.append({
                    'period': current_period,
                    'actual_spend': current_spend_str if current_spend_str else 'NULL',
                    'growth_percentage': 'NULL',
                    'MoM Growth': 'Must be flagged — not computed',
                    'formula_used': 'YoY: (current - previous_year) / previous_year * 100 [SKIPPED: NULL VALUE]',
                })
                continue
            
            try:
                current_spend = float(current_spend_str)
                previous_spend = float(previous_spend_str)
                
                if previous_spend == 0:
                    growth_pct = None
                    growth_percentage = 'UNDEFINED'
                    mom_growth = 'UNDEFINED'
                else:
                    growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
                    growth_percentage = f"{growth_pct:+.1f}%"
                    mom_growth = _annotate_growth_value(growth_pct, growth_type)
                
                result.append({
                    'period': current_period,
                    'actual_spend': f"{current_spend:.1f}",
                    'growth_percentage': growth_percentage,
                    'MoM Growth': mom_growth,
                    'formula_used': f"YoY: ({current_spend:.1f} - {previous_spend:.1f}) / {previous_spend:.1f} * 100",
                })
            except ValueError as e:
                raise ValueError(f"Invalid actual_spend value for {current_period}: {e}")
    
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description='UC-0C Budget Growth Calculator')
    parser.add_argument('--input', required=True, help='Path to ward_budget.csv')
    parser.add_argument('--ward', required=True, help='Ward name to filter by')
    parser.add_argument('--category', required=True, help='Category name to filter by')
    parser.add_argument('--growth-type', required=False, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Path to write output CSV')
    
    args = parser.parse_args()
    
    if not args.growth_type:
        sys.stderr.write("ERROR: --growth-type is required. Please specify 'MoM' or 'YoY'.\n")
        sys.exit(1)
    
    try:
        dataset, null_rows = load_dataset(args.input)
        growth_results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', newline='', encoding='utf-8') as outf:
            fieldnames = ['period', 'actual_spend', 'growth_percentage', 'MoM Growth']
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()
            for row in growth_results:
                writer.writerow({
                    'period': row.get('period', ''),
                    'actual_spend': row.get('actual_spend', ''),
                    'growth_percentage': row.get('growth_percentage', ''),
                    'MoM Growth': row.get('MoM Growth', ''),
                })
                sys.stderr.write(f"Formula for {row.get('period', '')}: {row.get('formula_used', '')}\n")
        
        print(f"Done. Growth analysis written to {args.output}")
    
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

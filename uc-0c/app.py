"""
UC-0C app.py — Budget Growth Calculator
Implemented using agents.md and skills.md.
"""
import argparse
import csv
from typing import List, Dict, Tuple

def load_dataset(file_path: str) -> Tuple[List[Dict], str]:
    """
    Reads CSV, validates columns, reports null count and which rows.
    Returns: (data, null_report)
    """
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_rows = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Missing required columns: {required_columns - set(reader.fieldnames or [])}")
            for row in reader:
                data.append(row)
                if not row.get('actual_spend', '').strip():
                    null_rows.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row.get('notes', '')
                    })
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {file_path} not found")
    except Exception as e:
        raise RuntimeError(f"Error loading dataset: {str(e)}")
    
    null_report = f"Found {len(null_rows)} null actual_spend rows:\n"
    for nr in null_rows:
        null_report += f"- {nr['period']} · {nr['ward']} · {nr['category']}: {nr['notes']}\n"
    
    return data, null_report

def compute_growth(ward: str, category: str, growth_type: str, data: List[Dict]) -> List[Dict]:
    """
    Computes growth for specific ward and category.
    Returns list of dicts: period, actual_spend, growth_percentage, formula_used, null_flag
    """
    if growth_type != 'MoM':
        raise ValueError("Only 'MoM' growth type is supported. Please specify --growth-type MoM")
    
    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    for row in filtered:
        period = row['period']
        spend_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')
        
        if not spend_str:
            results.append({
                'period': period,
                'actual_spend': '',
                'growth_percentage': '',
                'formula_used': '',
                'null_flag': f"NULL: {notes}"
            })
            prev_spend = None  # Reset for next calculation
            continue
        
        try:
            spend = float(spend_str)
        except ValueError:
            results.append({
                'period': period,
                'actual_spend': spend_str,
                'growth_percentage': '',
                'formula_used': '',
                'null_flag': f"INVALID: {notes}"
            })
            prev_spend = None
            continue
        
        growth = None
        formula = "MoM growth = ((current - previous) / previous) * 100" if prev_spend is not None else "No previous period for MoM calculation"
        if prev_spend is not None and prev_spend != 0:
            growth = ((spend - prev_spend) / prev_spend) * 100
        
        results.append({
            'period': period,
            'actual_spend': spend,
            'growth_percentage': f"{growth:.1f}%" if growth is not None else '',
            'formula_used': formula,
            'null_flag': ''
        })
        prev_spend = spend
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    if args.growth_type != 'MoM':
        print("Error: Only 'MoM' growth type is supported.")
        return
    
    data, null_report = load_dataset(args.input)
    print(null_report)
    
    results = compute_growth(args.ward, args.category, args.growth_type, data)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'actual_spend', 'growth_percentage', 'formula_used', 'null_flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Growth calculation completed. Results written to {args.output}")

if __name__ == "__main__":
    main()

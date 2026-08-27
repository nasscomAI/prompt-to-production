"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from typing import List, Dict

def load_dataset(file_path: str) -> List[Dict]:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    data = []
    null_rows = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"Missing required columns: {required_columns}")
            for row in reader:
                data.append(row)
                if not row.get('actual_spend') or row['actual_spend'].strip() == '':
                    null_rows.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row.get('notes', 'No notes')
                    })
        print(f"Dataset loaded: {len(data)} rows.")
        print(f"Null actual_spend count: {len(null_rows)}")
        if null_rows:
            print("Null rows:")
            for nr in null_rows:
                print(f"  {nr['period']} · {nr['ward']} · {nr['category']} · {nr['notes']}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")
    return data

def compute_growth(data: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """
    Filters for ward + category, computes growth, returns per-period table with formula.
    """
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError("Invalid growth_type. Must be 'MoM' or 'YoY'.")
    if not ward or not category:
        raise ValueError("Ward and category must be specified.")
    
    # Filter and sort
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_value = None
    for row in filtered:
        period = row['period']
        actual_spend_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')
        flag = None
        growth = None
        formula = None
        
        if not actual_spend_str:
            flag = f"Null: {notes}"
        else:
            try:
                current_value = float(actual_spend_str)
                if growth_type == 'MoM':
                    if prev_value is not None:
                        growth = ((current_value - prev_value) / prev_value) * 100
                        formula = f"MoM: (({current_value} - {prev_value}) / {prev_value}) * 100"
                    else:
                        formula = "MoM: No previous value for first period"
                    prev_value = current_value
                elif growth_type == 'YoY':
                    # YoY requires previous year data, which isn't available; raise error
                    raise ValueError("YoY growth not supported due to lack of previous year data.")
            except ValueError:
                flag = f"Invalid actual_spend value: {actual_spend_str}"
        
        results.append({
            'period': period,
            'actual_spend': actual_spend_str if actual_spend_str else 'NULL',
            'growth': f"{growth:.1f}%" if growth is not None else 'N/A',
            'formula': formula or 'N/A',
            'flag': flag or ''
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output growth_output.csv")
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth', 'formula', 'flag'])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Growth output written to {args.output}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
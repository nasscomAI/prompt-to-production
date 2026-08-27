"""
Budget Analysis Agent CLI (UC-0C)
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys
import logging
from typing import List, Dict

def load_dataset(file_path: str) -> List[Dict]:
    """Reads CSV, validates required columns, reports null count and which rows before returning."""
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    dataset = []
    null_rows = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])
            missing_cols = required_columns - headers
            if missing_cols:
                raise ValueError(f"Missing required columns in CSV: {missing_cols}")
                
            for row in reader:
                dataset.append(row)
                actual_spend = row.get('actual_spend', '').strip()
                if not actual_spend or actual_spend.lower() == 'null':
                    null_rows.append(row)
                    
    except FileNotFoundError:
        print(f"Error: Dataset not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Validation Error: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f"Validation Report: Found {len(null_rows)} null 'actual_spend' values before processing.")
        for r in null_rows:
            note = r.get('notes', 'Missing value')
            print(f"  - Null at Period: {r['period']}, Ward: {r['ward']}, Category: {r['category']} | Note: {note}")
    else:
        print("Validation Report: 0 null values found.")
        
    return dataset

def get_previous_period(period: str, growth_type: str) -> str:
    """Calculates the previous period dynamically based on growth-type (MoM or YoY)."""
    try:
        y, m = map(int, period.split('-'))
        if growth_type == 'MoM':
            m -= 1
            if m == 0:
                m = 12
                y -= 1
            return f"{y:04d}-{m:02d}"
        elif growth_type == 'YoY':
            return f"{y - 1:04d}-{m:02d}"
    except ValueError:
        pass
    return ""

def compute_growth(dataset: List[Dict], target_ward: str, target_category: str, growth_type: str) -> List[Dict]:
    """Computes growth metrics per period, flagging missing actual_spend and outputting formula."""
    
    # 1. Enforce: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if target_ward.lower() in ('all', 'any', '*') or target_category.lower() in ('all', 'any', '*'):
        print("Error: Aggregation across different wards or categories is strictly prohibited. Refusal constraint triggered.")
        sys.exit(1)
        
    # Filter dataset objectively for the specific ward and category
    filtered = [
        row for row in dataset
        if row['ward'].strip().lower() == target_ward.strip().lower() and 
           row['category'].strip().lower() == target_category.strip().lower()
    ]
    
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    lookup = {row['period']: row for row in filtered}
    result = []
    
    for row in filtered:
        period = row['period']
        actual_spend_raw = row['actual_spend'].strip()
        
        # Base row structure that honors required output format
        out_row = {
            'period': period,
            'ward': row['ward'],
            'category': row['category'],
            'budgeted_amount': row['budgeted_amount'],
            'actual_spend': actual_spend_raw if actual_spend_raw.lower() != 'null' else 'NULL',
            'growth_percentage': 'n/a',
            'formula_used': 'n/a',
            'flag_note': row.get('notes', '')
        }
        
        # 2. Flag every null actual_spend row before computing — report null reason from the notes column
        if not actual_spend_raw or actual_spend_raw.lower() == 'null':
            note = row.get('notes', 'Unspecified reason')
            out_row['formula_used'] = f"Missing value: {note} (Not Calculated)"
            out_row['growth_percentage'] = 'NULL (Flagged)'
            result.append(out_row)
            continue
            
        current_val = float(actual_spend_raw)
        prev_period = get_previous_period(period, growth_type)
        prev_row = lookup.get(prev_period)
        
        # 3. Show formula used in every output row alongside the result
        if not prev_row:
            if growth_type == 'MoM':
                out_row['formula_used'] = "No previous month data"
            else:
                out_row['formula_used'] = "No previous period data"
            out_row['growth_percentage'] = 'n/a'
        else:
            prev_spend_raw = prev_row['actual_spend'].strip()
            if not prev_spend_raw or prev_spend_raw.lower() == 'null':
                out_row['formula_used'] = f"Prior period ({prev_period}) value was NULL. Computation impossible."
                out_row['growth_percentage'] = 'n/a'
            else:
                prev_val = float(prev_spend_raw)
                if prev_val == 0:
                    out_row['formula_used'] = f"({current_val} - 0) / 0 * 100"
                    out_row['growth_percentage'] = 'Infinite'
                else:
                    growth_pct = ((current_val - prev_val) / prev_val) * 100
                    sign = '+' if growth_pct > 0 else ''
                    out_row['growth_percentage'] = f"{sign}{growth_pct:.1f}%"
                    out_row['formula_used'] = f"({current_val} - {prev_val}) / {prev_val} * 100"
                    
        result.append(out_row)
        
    return result

def main():
    parser = argparse.ArgumentParser(description="Budget Analysis Agent CLI")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", help="Growth type to calculate (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    # 4. If --growth-type not specified — refuse and ask, never guess
    if getattr(args, 'growth_type', None) is None:
        print("Error: --growth-type was NOT specified.")
        print("Enforcement Rule: Refusing to guess metric logic. Please specifically ask with '--growth-type MoM' or YoY.")
        sys.exit(1)
        
    if args.growth_type not in ('MoM', 'YoY'):
        print(f"Error: Unsupported growth type '{args.growth_type}'. Use 'MoM' or 'YoY'.")
        sys.exit(1)

    print("--- Starting Budget Analysis ---")
    dataset = load_dataset(args.input)
    
    print("\nComputing growth metrics...")
    growth_results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if not growth_results:
        print(f"Warning: No valid records found matching Ward: '{args.ward}' and Category: '{args.category}'.")
    else:
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_percentage', 'formula_used', 'flag_note']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in growth_results:
                    writer.writerow(row)
            print(f"Success: Analysis finalized. Wrote {len(growth_results)} records to {args.output}")
            
        except Exception as e:
            print(f"Error writing to output file {args.output}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

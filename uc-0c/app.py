"""
UC-0C app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys
import os

def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found at {file_path}")
        
    rows = []
    null_rows = []
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # Line 1 is headers
            actual = row.get('actual_spend', '').strip()
            # Parse actual_spend as float, handle empty/null
            if actual == '' or actual.lower() == 'null':
                row['actual_spend'] = None
                null_rows.append((i, row.get('period'), row.get('ward'), row.get('category'), row.get('notes')))
            else:
                try:
                    row['actual_spend'] = float(actual)
                except ValueError:
                    row['actual_spend'] = None
                    null_rows.append((i, row.get('period'), row.get('ward'), row.get('category'), row.get('notes')))
            rows.append(row)
            
    print(f"Dataset loaded. Total rows: {len(rows)}. Deliberate null values detected: {len(null_rows)}")
    for line, period, ward, cat, notes in null_rows:
        print(f"  - Line {line}: Null spend in {period} for {ward} ({cat}). Reason: '{notes}'")
        
    return rows, null_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name (refuses if 'All' or 'Any')")
    parser.add_argument("--category", required=True, help="Category name (refuses if 'All' or 'Any')")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write growth results CSV")
    args = parser.parse_args()
    
    # Enforcement 4: Growth type must be specified
    if not args.growth_type:
        print("Error: --growth-type must be explicitly specified (e.g. MoM). Guessing is prohibited.", file=sys.stderr)
        sys.exit(1)
        
    growth_type = args.growth_type.strip()
    if growth_type not in ['MoM', 'YoY']:
        print(f"Error: Unsupported growth-type '{growth_type}'. Only MoM or YoY are allowed.", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement 1: Refuse aggregation across wards or categories
    ward = args.ward.strip()
    category = args.category.strip()
    if ward.lower() in ['all', 'any', '*'] or category.lower() in ['all', 'any', '*']:
        print("Error: Aggregation across multiple wards or categories is strictly prohibited. Requests for 'All' or 'Any' are refused.", file=sys.stderr)
        sys.exit(1)
        
    # Load dataset
    rows, null_records = load_dataset(args.input)
    
    # Filter dataset for requested ward and category
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    if not filtered:
        print(f"No records found matching ward '{ward}' and category '{category}'.", file=sys.stderr)
        sys.exit(1)
        
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for idx, current_row in enumerate(filtered):
        period = current_row['period']
        curr_spend = current_row['actual_spend']
        notes = current_row.get('notes', '')
        
        # Default empty growth / formula
        growth = "NULL"
        formula = "N/A"
        
        if curr_spend is None:
            # Enforcement 2: Flag null row and report notes reason
            growth = "NULL"
            formula = f"N/A (Null value encountered: {notes})"
            actual_disp = "NULL"
        else:
            actual_disp = f"{curr_spend:.1f}"
            if idx == 0:
                growth = "N/A"
                formula = "First period in dataset (no prior period to compare)"
            else:
                prev_row = filtered[idx - 1]
                prev_spend = prev_row['actual_spend']
                
                if prev_spend is None:
                    growth = "NULL"
                    formula = f"N/A (Prior period spend is NULL: {prev_row.get('notes', '')})"
                else:
                    diff = curr_spend - prev_spend
                    growth_val = diff / prev_spend
                    sign = "+" if growth_val >= 0 else ""
                    growth = f"{sign}{growth_val*100:.1f}%"
                    # Enforcement 3: Show formula used in every output row
                    formula = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
                    
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_disp,
            'growth': growth,
            'formula': formula,
            'notes': notes if curr_spend is None else ''
        })
        
    # Write output CSV
    headers = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
    with open(args.output, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Growth calculation completed successfully. Results written to {args.output}")

if __name__ == "__main__":
    main()

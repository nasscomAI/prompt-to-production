"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

def load_dataset(input_path: str):
    """
    Load CSV, validate columns, report nulls.
    Returns list of dicts.
    """
    data = []
    null_count = 0
    null_rows = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                data.append(row)
                if not row.get('actual_spend', '').strip():
                    null_count += 1
                    null_rows.append(f"Row {i}: {row.get('period', '')} {row.get('ward', '')} {row.get('category', '')}")
        print(f"Loaded {len(data)} rows. Null actual_spend: {null_count}")
        if null_rows:
            print("Null rows:")
            for nr in null_rows:
                print(nr)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []
    return data

def compute_growth(data, ward, category, growth_type, output_path):
    """
    Filter data, compute growth, write output.
    """
    if growth_type != 'MoM':
        print("Refusing: growth-type not specified or not MoM")
        return
    
    filtered = [row for row in data if row.get('ward') == ward and row.get('category') == category]
    if not filtered:
        print(f"No data for ward {ward} and category {category}")
        return
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    for row in filtered:
        period = row['period']
        spend_str = row.get('actual_spend', '').strip()
        if not spend_str:
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'mom_growth': 'NULL',
                'formula': 'NULL (no data)',
                'flag': 'NULL flagged'
            })
            continue
        try:
            spend = float(spend_str)
            if prev_spend is not None:
                growth = ((spend - prev_spend) / prev_spend) * 100
                formula = f"(({spend} - {prev_spend}) / {prev_spend}) * 100 = {growth:.1f}%"
                mom_growth = f"{growth:.1f}%"
            else:
                mom_growth = 'N/A'
                formula = 'First period'
            results.append({
                'period': period,
                'actual_spend': spend,
                'mom_growth': mom_growth,
                'formula': formula,
                'flag': ''
            })
            prev_spend = spend
        except ValueError:
            results.append({
                'period': period,
                'actual_spend': spend_str,
                'mom_growth': 'Error',
                'formula': 'Invalid number',
                'flag': 'Error'
            })
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'mom_growth', 'formula', 'flag'])
            writer.writeheader()
            writer.writerows(results)
        print(f"Output written to {output_path}")
    except Exception as e:
        print(f"Error writing output: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    if data:
        compute_growth(data, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()

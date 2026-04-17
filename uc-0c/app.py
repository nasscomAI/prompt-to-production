"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath):
    data = []
    null_count = 0
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if not row['actual_spend'].strip():
                    null_count += 1
                    null_rows.append(i + 2) # 1-based index including header
                data.append(row)
                
        print(f"Loaded dataset. Found {null_count} null actual_spend values at rows: {null_rows}")
        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)


def compute_growth(data, ward, category, growth_type):
    if not ward or ward.lower() == 'any' or not category or category.lower() == 'any':
        print("REFUSED: Never aggregate across wards or categories unless explicitly instructed. Please provide specific ward and category.")
        sys.exit(1)
        
    if not growth_type:
        print("REFUSED: --growth-type not specified. Never guess.")
        sys.exit(1)
        
    if growth_type.upper() != 'MOM':
        print(f"Only MoM is implemented in this example, requested: {growth_type}")
        sys.exit(1)

    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        formula = ""
        growth_str = ""
        flag = ""
        
        if not actual_str:
            flag = f"NULL FLAGGED: {notes}" if notes else "NULL FLAGGED"
            growth_str = "N/A"
            formula = "N/A (Missing data)"
            prev_spend = None # Break the chain
        else:
            current_spend = float(actual_str)
            if prev_spend is not None:
                growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth_val > 0 else ""
                growth_str = f"{sign}{growth_val:.1f}%"
                formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                growth_str = "N/A"
                formula = "N/A (No previous data)"
            
            prev_spend = current_spend
            
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_str if actual_str else "NULL",
            'growth_percent': growth_str,
            'formula': formula,
            'flag': flag
        })
        
    return results


def format_growth_report(results, output_path):
    if not results:
        print("No results to write.")
        return
        
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_percent', 'formula', 'flag']
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Report written to {output_path}")
    except Exception as e:
        print(f"Error writing report: {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--ward", help="Specific ward to filter by")
    parser.add_argument("--category", help="Specific category to filter by")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("REFUSED: --growth-type must be explicitly provided. System will not guess.")
        sys.exit(1)
        
    if not args.ward or args.ward.lower() == 'any' or not args.category or args.category.lower() == 'any':
        print("REFUSED: Cannot aggregate across wards or categories. Please provide specific ward and category.")
        sys.exit(1)

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    format_growth_report(results, args.output)

if __name__ == "__main__":
    main()

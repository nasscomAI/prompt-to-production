import argparse
import csv
import sys
from collections import defaultdict

def load_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return data
    except FileNotFoundError:
        print(f"Error: dataset {filepath} not found.")
        sys.exit(1)

def compute_growth(data, target_ward, target_category, growth_type):
    if not growth_type:
        print("ERROR: Refusal Condition Met. Growth-type is not specified. Refusing to guess or assume the aggregation level.")
        sys.exit(1)

    if str(target_ward).lower() == "all" or str(target_category).lower() == "all":
        print("ERROR: Refusal Condition Met. Instructed to aggregate across wards or categories. Refused.")
        sys.exit(1)

    # Group data by (ward, category) to prevent cross-aggregation
    groups = defaultdict(list)
    for row in data:
        # If targeting specific ward/cat, filter them out early
        if target_ward and row['ward'] != target_ward: continue
        if target_category and row['category'] != target_category: continue
        
        groups[(row['ward'], row['category'])].append(row)

    if not groups:
        print("No data matched the given ward/category selection.")
        sys.exit(1)

    results = []
    
    for (ward, category), rows in groups.items():
        # Sort by period just in case
        rows = sorted(rows, key=lambda x: x['period'])
        
        prev_spend = None
        for i, row in enumerate(rows):
            period = row['period']
            raw_spend = row['actual_spend'].strip()
            notes = row['notes'].strip()
            
            result_row = {
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': raw_spend if raw_spend else 'NULL',
                'growth': '',
                'formula': '',
                'notes': notes
            }

            if not raw_spend:
                # Null condition
                result_row['growth'] = 'FLAGGED'
                result_row['formula'] = 'n/a'
                result_row['notes'] = f"Missing data: {notes}"
                prev_spend = None  # breaks the chain for next period
            else:
                current_spend = float(raw_spend)
                if prev_spend is not None:
                    if prev_spend == 0:
                        result_row['growth'] = 'N/A (Div by Zero)'
                        result_row['formula'] = f"({current_spend} - 0) / 0"
                    else:
                        g = ((current_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if g > 0 else ""
                        result_row['growth'] = f"{sign}{g:.1f}%"
                        result_row['formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                else:
                    if i == 0:
                        result_row['growth'] = 'n/a (first period)'
                    else:
                        result_row['growth'] = 'n/a (prior period null)'
                    result_row['formula'] = 'n/a'
                    
                prev_spend = current_spend

            results.append(result_row)
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", required=False, help="Specific ward to compute")
    parser.add_argument("--category", required=False, help="Specific category")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    args = parser.parse_args()

    # Pre-check growth type (Error handling to satisfy RICE intent)
    if not args.growth_type:
        print("ERROR: --growth-type must be specified explicitly (e.g., MoM). Refusing to act on ambiguous requests.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    
    # Null scan reporting (as requested by skills.md)
    null_rows = [r for r in data if not r['actual_spend'].strip()]
    print(f"Pre-computation scan: Found {len(null_rows)} null actual_spend rows.")
    for nr in null_rows:
        print(f" - [{nr['period']}] {nr['ward']} | {nr['category']} -> NULL ({nr['notes']})")

    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth', 'formula', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Output successfully written to {args.output}")

if __name__ == "__main__":
    main()

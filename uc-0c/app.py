"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def compute_growth(input_path, ward, category, growth_type, output_path):
    # Rule 1 & Rule 4: Refuse hidden aggregations or assumed growth formulas
    if not ward or not category:
        print("REFUSAL: Cannot aggregate across wards or categories. Please specify --ward and --category.")
        sys.exit(1)
        
    if not growth_type:
        print("REFUSAL: --growth-type not specified. Will not guess the formula.")
        sys.exit(1)

    filtered_data = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == ward and row['category'] == category:
                filtered_data.append(row)

    filtered_data.sort(key=lambda x: x['period'])

    results = []
    for i, current in enumerate(filtered_data):
        period = current['period']
        notes = current['notes']
        
        # Rule 2: Flag every null row before computing
        if not current['actual_spend'].strip():
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': f"FLAGGED NULL: {notes}",
                'formula_used': 'N/A'
            })
            continue

        actual_spend = float(current['actual_spend'])
        
        if growth_type == 'MoM':
            if i == 0:
                growth_str = "n/a"
                formula = "N/A (first period)"
            else:
                prev = filtered_data[i-1]
                if not prev['actual_spend'].strip():
                    growth_str = "N/A (previous month is NULL)"
                    formula = f"({actual_spend} - NULL) / NULL"
                else:
                    prev_spend = float(prev['actual_spend'])
                    if prev_spend == 0:
                        growth_str = "Infinity"
                        formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                    else:
                        growth = ((actual_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if growth > 0 else ""
                        # Add notes text if present
                        note_suffix = f" ({notes})" if notes else ""
                        growth_str = f"{sign}{growth:.1f}%{note_suffix}".strip()
                        # Rule 3: Show formula used in every output row
                        formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                        
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': actual_spend,
                'growth': growth_str,
                'formula_used': formula
            })
        else:
            print(f"REFUSAL: Unsupported growth type '{growth_type}'. Cannot compute.")
            sys.exit(1)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth', 'formula_used'])
        writer.writeheader()
        writer.writerows(results)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    # Marking these optional to manually handle and enforce refusal logic natively
    parser.add_argument("--ward", required=False, help="Ward filter")
    parser.add_argument("--category", required=False, help="Category filter")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g., MoM)")
    args = parser.parse_args()
    
    compute_growth(args.input, args.ward, args.category, args.growth_type, args.output)
    print(f"Done. Growth logic applied and written to {args.output}")

if __name__ == "__main__":
    main()

import argparse
import csv
import sys

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Growth type (must be MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    if not args.ward or not args.category:
        print("Error: Never aggregate across wards or categories — refuse if no --ward or --category specified")
        sys.exit(1)

    if not args.growth_type:
        print("Error: If --growth-type not specified — refuse and ask, never guess")
        sys.exit(1)

    if args.growth_type != "MoM":
        print("Error: Only MoM growth is supported.")
        sys.exit(1)

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: File {args.input} not found.")
        sys.exit(1)

    filtered_data = [row for row in data if row['ward'] == args.ward and row['category'] == args.category]
    filtered_data.sort(key=lambda x: x['period'])

    output_rows = []
    previous_spend = None

    for row in filtered_data:
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        out_row = {
            'period': period,
            'ward': args.ward,
            'category': args.category,
            'actual_spend': actual_spend_str,
            'previous_spend': '',
            'growth_pct': '',
            'formula': '',
            'flag': ''
        }
        
        if not actual_spend_str:
            out_row['flag'] = notes
            previous_spend = None
        else:
            try:
                current_spend = float(actual_spend_str)
            except ValueError:
                out_row['flag'] = 'Invalid actual_spend'
                current_spend = None
            
            if current_spend is not None:
                if previous_spend is not None:
                    out_row['previous_spend'] = f"{previous_spend:.1f}"
                    growth = (current_spend - previous_spend) / previous_spend * 100
                    out_row['growth_pct'] = f"{growth:+.1f}%"
                    out_row['formula'] = f"({current_spend} - {previous_spend}) / {previous_spend} * 100"
                
                previous_spend = current_spend
        
        output_rows.append(out_row)

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'previous_spend', 'growth_pct', 'formula', 'flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()

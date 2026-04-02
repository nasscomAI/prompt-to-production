"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import sys

def load_dataset(filepath, ward, category):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == ward and row['category'] == category:
                data.append(row)
    data.sort(key=lambda x: x['period'])
    return data

def compute_growth(data, args):
    output_rows = []
    prev_spend = None
    
    for row in data:
        period = row['period']
        actual = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')
        
        # 2. Flag every null row before computing
        if not actual or actual.lower() == 'null':
            print(f"FLAG: Null detected for {period}. Reason from notes: {notes}")
            output_rows.append({
                "Ward": args.ward,
                "Category": args.category,
                "Period": period,
                "Actual Spend": "NULL",
                "Growth": "Must be flagged - not computed",
                "Formula": "N/A"
            })
            prev_spend = None
            continue
            
        current_spend = float(actual)
        
        if prev_spend is None:
            growth = "N/A"
            formula = "Base Month"
        else:
            if args.growth_type.lower() == "mom":
                pct = ((current_spend - prev_spend) / prev_spend) * 100
                growth = f"{pct:+.1f}%"
                formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            else:
                growth = "N/A"
                formula = "Unknown Formula Type"
                
        output_rows.append({
            "Ward": args.ward,
            "Category": args.category,
            "Period": period,
            "Actual Spend": current_spend,
            "Growth": growth,
            "Formula": formula
        })
        prev_spend = current_spend

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # 4. If --growth-type not specified — refuse
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. I cannot guess the formula. Please explicitly provide it.")
        sys.exit(1)
        
    # 1. Never aggregate across wards or categories unless explicitly instructed — refuse
    if not args.ward or not args.category or args.ward.lower() == "all" or args.category.lower() == "all":
        print("REFUSAL: You must specify a specific --ward and --category. Aggregation without scope isolation is denied.")
        sys.exit(1)

    data = load_dataset(args.input, args.ward, args.category)
    output_rows = compute_growth(data, args)

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Ward", "Category", "Period", "Actual Spend", "Growth", "Formula"])
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Done. Output successfully written to {args.output}")

if __name__ == "__main__":
    main()

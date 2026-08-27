"""
UC-0C app.py
Number That Looks Right
"""
import argparse
import csv
import sys

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False) # deliberately false to catch and refuse
    args = parser.parse_args()

    if not args.growth_type:
        print("Refused: --growth-type must be specified. Never guess.")
        sys.exit(1)

    if args.ward.lower() in ["any", "all", ""]:
        print("Refused: Cannot aggregate across all wards.")
        sys.exit(1)

    if args.category.lower() in ["any", "all", ""]:
        print("Refused: Cannot aggregate across all categories.")
        sys.exit(1)

    # load data
    rows = []
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == args.ward and row['category'] == args.category:
                rows.append(row)

    # sort by period just in case
    rows.sort(key=lambda x: x['period'])

    output_rows = []
    prev_actual_spend = None

    for r in rows:
        period = r['period']
        actual_spend_str = r['actual_spend'].strip()
        notes = r['notes']

        # Determine value
        if not actual_spend_str:
            actual_spend = None
        else:
            try:
                actual_spend = float(actual_spend_str)
            except:
                actual_spend = None

        growth_val = "NULL"
        formula = "n/a"
        flag = ""

        if actual_spend is None:
            flag = f"Must be flagged — not computed. Note: {notes}"
            prev_actual_spend = None # break the chain
        else:
            if prev_actual_spend is not None:
                if prev_actual_spend == 0:
                    growth_val = "Undefined"
                else:
                    growth = (actual_spend - prev_actual_spend) / prev_actual_spend * 100
                    sign = "+" if growth > 0 else ""
                    growth_val = f"{sign}{growth:.1f}%"
                formula = f"({actual_spend} - {prev_actual_spend}) / {prev_actual_spend} * 100"
            else:
                growth_val = "n/a"
                formula = "n/a (no previous period)"
            
            prev_actual_spend = actual_spend

        output_rows.append({
            "ward": args.ward,
            "category": args.category,
            "period": period,
            "actual_spend": actual_spend_str if actual_spend_str else "NULL",
            "MoM Growth": growth_val,
            "formula": formula,
            "flag": flag
        })

    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "period", "actual_spend", "MoM Growth", "formula", "flag"])
        writer.writeheader()
        writer.writerows(output_rows)
    
    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()

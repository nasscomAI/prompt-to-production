"""
UC-0C app.py — Ward Budget Aggregator
Groups ward_budget.csv by ward + category, sums actual_spend.
Missing values are excluded (not zero-filled) and flagged.
Usage: python app.py --input ../data/budget/ward_budget.csv --output growth_output.csv
"""
import argparse
import csv
from collections import defaultdict

def aggregate_budget(input_path: str, output_path: str):
    """
    Read ward_budget.csv, group by (ward, category), sum actual_spend.
    Exclude blank actual_spend entries and annotate count of missing months.
    Write results to output_path.
    """
    totals   = defaultdict(float)
    missing  = defaultdict(int)

    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ward   = row['ward'].strip()
            cat    = row['category'].strip()
            actual = row['actual_spend'].strip()
            key    = (ward, cat)
            if actual == '':
                missing[key] += 1
            else:
                totals[key] += float(actual)

    all_keys = sorted(set(list(totals.keys()) + list(missing.keys())),
                      key=lambda x: (x[0], x[1]))

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ward', 'category', 'total_actual_spend', 'missing_months', 'note'])
        for key in all_keys:
            ward, cat = key
            total  = round(totals[key], 1)
            missed = missing[key]
            note   = (f"{missed} month(s) excluded — actual_spend not reported"
                      if missed > 0 else "")
            writer.writerow([ward, cat, total, missed, note])

    print(f"Done. {len(all_keys)} groups written to {output_path}")
    if any(missing.values()):
        print(f"Warning: {sum(missing.values())} missing actual_spend entries excluded from totals.")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Aggregator")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write aggregated CSV")
    args = parser.parse_args()
    aggregate_budget(args.input, args.output)

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

def load_dataset(input_path):
    rows = []
    null_rows = []
    with open(input_path, newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            rows.append(row)
            if row['actual_spend'] == '' or row['actual_spend'].lower() == 'null':
                null_rows.append(row)
    return rows, null_rows

def compute_growth(rows, ward, category, growth_type):
    result = []
    prev_spend = None
    for row in rows:
        if row['ward'] == ward and row['category'] == category:
            period = row['period']
            actual = row['actual_spend']
            formula = f"{growth_type} growth"
            if actual == '' or actual.lower() == 'null':
                result.append({
                    "period": period,
                    "actual_spend": "NULL",
                    "growth": "FLAGGED",
                    "formula": formula,
                    "reason": row.get("notes", "")
                })
                prev_spend = None
            else:
                actual = float(actual)
                if prev_spend is not None:
                    growth = ((actual - prev_spend) / prev_spend) * 100
                else:
                    growth = None
                result.append({
                    "period": period,
                    "actual_spend": actual,
                    "growth": f"{growth:.1f}%" if growth is not None else "",
                    "formula": formula,
                    "reason": ""
                })
                prev_spend = actual
    return result

def main():
    import sys
    input_path = sys.argv[1]
    ward = sys.argv[2]
    category = sys.argv[3]
    growth_type = sys.argv[4]
    output_path = sys.argv[5]
    rows, null_rows = load_dataset(input_path)
    table = compute_growth(rows, ward, category, growth_type)
    with open(output_path, 'w', newline='') as outfile:
        fieldnames = ["period", "actual_spend", "growth", "formula", "reason"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in table:
            writer.writerow(row)

if __name__ == "__main__":
    main()

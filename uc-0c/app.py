"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

# Skill: load_dataset
def load_dataset(file_path):
    dataset = []
    null_rows = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset.append(row)
            if row['actual_spend'] == '' or row['actual_spend'].lower() == 'null':
                null_rows.append({'period': row['period'], 'ward': row['ward'], 'category': row['category'], 'notes': row['notes']})
    return dataset, null_rows

# Skill: compute_growth
def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        return [{'period': '', 'actual_spend': '', 'growth': 'Refused: growth-type not specified.', 'formula': '', 'notes': ''}]
    if ward.lower() == 'all' or category.lower() == 'all':
        return [{'period': '', 'actual_spend': '', 'growth': 'Refused: aggregation across wards or categories not permitted.', 'formula': '', 'notes': ''}]
    rows = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    output = []
    prev_spend = None
    for row in rows:
        period = row['period']
        actual = row['actual_spend']
        formula = ''
        if actual == '' or actual.lower() == 'null':
            output.append({'period': period, 'actual_spend': 'NULL', 'growth': 'Must be flagged—not computed', 'formula': '', 'notes': row['notes']})
            prev_spend = None
            continue
        actual = float(actual)
        if growth_type == 'MoM' and prev_spend is not None:
            growth = ((actual - prev_spend) / prev_spend) * 100 if prev_spend != 0 else 0
            formula = f"MoM: ({actual} - {prev_spend}) / {prev_spend} * 100"
            output.append({'period': period, 'actual_spend': actual, 'growth': f"{growth:+.1f}%", 'formula': formula, 'notes': row['notes']})
        else:
            output.append({'period': period, 'actual_spend': actual, 'growth': 'n/a', 'formula': 'First period or missing previous', 'notes': row['notes']})
        prev_spend = actual
    # Add flagged null rows that were not in the filtered rows
    dataset_nulls = [r for r in dataset if (r['actual_spend'] == '' or r['actual_spend'].lower() == 'null') and (r['ward'] == ward and r['category'] == category)]
    for r in dataset_nulls:
        if not any(o['period'] == r['period'] for o in output):
            output.append({'period': r['period'], 'actual_spend': 'NULL', 'growth': 'Must be flagged—not computed', 'formula': '', 'notes': r['notes']})
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    dataset, null_rows = load_dataset(args.input)
    result = compute_growth(dataset, args.ward, args.category, args.growth_type)
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth', 'formula', 'notes'])
        writer.writeheader()
        for row in result:
            writer.writerow(row)
    print(f"Growth output written to {args.output}")
    if null_rows:
        print("Null rows flagged:")
        for nr in null_rows:
            print(nr)

if __name__ == "__main__":
    main()

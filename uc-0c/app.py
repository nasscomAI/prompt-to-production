"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os

def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("CSV file not found")

    data = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def compute_growth(data, ward, category):
    # Filter data correctly
    filtered = [
        row for row in data
        if row['ward'] == ward and row['category'] == category
    ]

    if len(filtered) < 2:
        raise ValueError("Not enough data")

    values = []

    for row in filtered:
        spend = row['actual_spend']

        # Handle missing values (IMPORTANT)
        if spend is None or spend == "":
            continue

        try:
            values.append(float(spend))
        except:
            continue

    if len(values) < 2:
        raise ValueError("Not enough valid data for growth")

    # Month-over-month growth
    prev = values[-2]
    curr = values[-1]

    if prev == 0:
        raise ValueError("Previous value is zero")

    growth = ((curr - prev) / prev) * 100
    return growth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    try:
        data = load_dataset(args.input)
        growth = compute_growth(data, args.ward, args.category)

        with open(args.output, 'w', encoding='utf-8') as file:
            file.write(f"Growth: {growth:.2f}%")

        print("✅ Growth calculated successfully!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
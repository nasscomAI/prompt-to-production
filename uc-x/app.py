"""
UC-X app.py — Example implementation
Processes CSV data and prints filtered results.
"""

import argparse
import csv


def load_data(file_path):
    rows = []
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def analyze_data(rows, column, value):
    results = []
    for r in rows:
        if r.get(column) == value:
            results.append(r)
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-X Data Analyzer")

    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--column", required=True, help="Column to filter")
    parser.add_argument("--value", required=True, help="Value to match")

    args = parser.parse_args()

    data = load_data(args.input)
    results = analyze_data(data, args.column, args.value)

    print("Results:")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()

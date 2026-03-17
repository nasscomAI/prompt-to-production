"""
UC-0C — Ward Budget Lookup
"""

import csv
import argparse


def load_budget(file_path):

    data = []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data.append(row)

    return data


def find_budget(data, ward):

    for row in data:
        if row["ward"].lower() == ward.lower():
            return row

    return None


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--file", required=True)
    parser.add_argument("--ward", required=True)

    args = parser.parse_args()

    data = load_budget(args.file)

    result = find_budget(data, args.ward)

    if result:
        print("Ward Budget Details:")
        print(result)
    else:
        print("Ward not found. NEEDS_REVIEW")


if __name__ == "__main__":
    main()
"""
UC-0C — Number That Looks Right

BASELINE RUN. This is the naive prompt turned into code:
"Calculate growth from the data."

It reads the whole file, adds everything up, picks month-on-month because that
is the obvious default, skips the blank cells, and prints one confident number.
Every one of those decisions is wrong, and none of them announces itself.

Committed as-is so the failure is on the record before it is fixed.

Usage:
    python app.py --input ../data/budget/ward_budget.csv --output growth_output.csv
"""

import argparse
import csv
import os
import sys


class DatasetError(Exception):
    """Raised when the input file cannot be read or is missing required columns."""


REQUIRED_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes",
]


def load_dataset(path):
    """Read the CSV into a list of dicts."""
    if not os.path.isfile(path):
        raise DatasetError("Input file not found: {}".format(path))
    with open(path, "r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise DatasetError("No rows in {}".format(path))
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise DatasetError("Missing columns: {}".format(missing))
    return rows


def compute_growth(rows):
    """
    Total everything per period, then month-on-month growth on the totals.
    Blank actual_spend values are skipped so the sum still works.
    """
    totals = {}
    for row in rows:
        raw = row["actual_spend"].strip()
        if not raw:
            continue          # <- the silent null
        totals[row["period"]] = totals.get(row["period"], 0.0) + float(raw)

    periods = sorted(totals)
    out = []
    for index in range(1, len(periods)):
        prev, curr = periods[index - 1], periods[index]
        growth = (totals[curr] - totals[prev]) / totals[prev] * 100.0
        out.append({"period": curr, "total_spend": round(totals[curr], 2),
                    "growth_pct": round(growth, 1)})
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator (baseline)")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
    except DatasetError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 2

    results = compute_growth(rows)

    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["period", "total_spend", "growth_pct"])
        writer.writeheader()
        writer.writerows(results)

    average = sum(r["growth_pct"] for r in results) / len(results)
    print("Average growth across the dataset: {:+.1f}%".format(average))
    print("Written to {}".format(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())

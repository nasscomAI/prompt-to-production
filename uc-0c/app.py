"""
UC-0C — Number That Looks Right

CRAFT cycle 1 fix: wrong aggregation level.

The baseline returned +0.5% average growth across the whole dataset. That number
is arithmetically fine and analytically worthless — it averages five wards and
five categories together, so Ward 1's +33.1% monsoon road spike and its −34.8%
October collapse cancel against unrelated streetlight and parks spending and
vanish. Nobody can act on +0.5%.

Enforcement rule SCOPE now requires an explicit ward and category, and refuses
any request to aggregate across either.

Usage:
    python app.py --input ../data/budget/ward_budget.csv \
                  --ward "Ward 1 – Kasba" \
                  --category "Roads & Pothole Repair" \
                  --output growth_output.csv
"""

import argparse
import csv
import os
import sys


class DatasetError(Exception):
    """Raised when the input file cannot be read or is missing required columns."""


class ScopeRefusal(Exception):
    """Raised when the request would aggregate across wards or categories."""


REQUIRED_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes",
]

# agents.md / SCOPE — tokens that mean "collapse the breakdown".
AGGREGATION_TOKENS = ["all", "*", "any", "total", "overall", "everything", "combined"]


def load_dataset(path):
    """Read the CSV and confirm it has the columns this tool depends on."""
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


def distinct(rows, column):
    return sorted({row[column] for row in rows})


def check_scope(rows, ward, category):
    """
    agents.md / SCOPE — refuse aggregation, refuse unknown values.
    A refusal here is a successful outcome, not a failure to be worked around.
    """
    for label, value in (("--ward", ward), ("--category", category)):
        if value is None or not value.strip():
            raise ScopeRefusal(
                "{} was not supplied. This tool will not pick a scope for you, "
                "because a figure computed at the wrong level looks exactly like "
                "a figure computed at the right one.".format(label)
            )
        if value.strip().lower() in AGGREGATION_TOKENS:
            raise ScopeRefusal(
                "{}='{}' asks for an aggregate across the breakdown. Refused: "
                "growth is only meaningful per ward per category. Ask for one "
                "pair at a time.".format(label, value)
            )

    wards, categories = distinct(rows, "ward"), distinct(rows, "category")
    if ward not in wards:
        raise ScopeRefusal("Unknown ward '{}'. Known wards: {}".format(ward, wards))
    if category not in categories:
        raise ScopeRefusal(
            "Unknown category '{}'. Known categories: {}".format(category, categories)
        )


def compute_growth(rows, ward, category):
    """Per-period month-on-month growth for exactly one ward + category pair."""
    selected = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )

    results = []
    previous = None
    for row in selected:
        raw = row["actual_spend"].strip()
        if not raw:
            continue          # <- still silently skipped; fixed in cycle 2
        value = float(raw)
        growth = ""
        if previous is not None:
            growth = round((value - previous) / previous * 100.0, 1)
        results.append({
            "ward": ward,
            "category": category,
            "period": row["period"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": value,
            "growth_pct": growth,
        })
        previous = value
    return results


FIELDNAMES = ["ward", "category", "period", "budgeted_amount", "actual_spend", "growth_pct"]


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", help="Exactly one ward. Aggregate values are refused.")
    parser.add_argument("--category", help="Exactly one category. Aggregate values are refused.")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
    except DatasetError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 2

    try:
        check_scope(rows, args.ward, args.category)
    except ScopeRefusal as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 3

    results = compute_growth(rows, args.ward, args.category)

    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    print("{} rows written to {}".format(len(results), args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())

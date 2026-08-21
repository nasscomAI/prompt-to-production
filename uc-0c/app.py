"""
UC-0C — Number That Looks Right

CRAFT cycle 3 fix: formula assumption.

The baseline returned +0.5% average growth across the whole dataset. That number
is arithmetically fine and analytically worthless — it averages five wards and
five categories together, so Ward 1's +33.1% monsoon road spike and its −34.8%
October collapse cancel against unrelated streetlight and parks spending and
vanish. Nobody can act on +0.5%.

Enforcement rule SCOPE requires an explicit ward and category and refuses any
request to aggregate across either.

Cycle 2 then caught the second failure: the 5 deliberate null actual_spend rows
were being skipped, which silently bridged growth across the gap — Warje Roads
was computing August against June and presenting it as a month-on-month figure.
Enforcement rule NULL VISIBILITY now emits a row for every null with the reason
from the notes column, and refuses to compute growth against a null prior.

Cycle 3 caught the last one: MoM was hardcoded. Nothing ever asked which growth
figure was wanted, and a YoY question answered with a MoM number is wrong in a
way the output does not show. Enforcement rule FORMULA now requires
--growth-type explicitly, refuses to guess, and prints the arithmetic used in
every single row.

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


class FormulaRefusal(Exception):
    """Raised when the growth formula was not specified and would have to be guessed."""


REQUIRED_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes",
]

# agents.md / SCOPE — tokens that mean "collapse the breakdown".
AGGREGATION_TOKENS = ["all", "*", "any", "total", "overall", "everything", "combined"]

# agents.md / FORMULA — the growth types this tool knows, and the step in months
# between a period and the period it is compared against.
GROWTH_TYPES = {"MoM": 1, "YoY": 12}


def shift_period(period, months_back):
    """'2024-07' shifted back 1 month is '2024-06'; back 12 is '2023-07'."""
    year, month = period.split("-")
    index = int(year) * 12 + (int(month) - 1) - months_back
    return "{:04d}-{:02d}".format(index // 12, index % 12 + 1)


def check_formula(growth_type):
    """agents.md / FORMULA — refuse to pick the formula on the user's behalf."""
    if growth_type is None or not str(growth_type).strip():
        raise FormulaRefusal(
            "--growth-type was not specified. Refused rather than guessed: MoM and "
            "YoY answer different questions, and a YoY question answered with a MoM "
            "number is wrong in a way the output cannot show. Re-run with "
            "--growth-type MoM or --growth-type YoY."
        )
    if growth_type not in GROWTH_TYPES:
        raise FormulaRefusal(
            "Unknown --growth-type '{}'. Known types: {}".format(
                growth_type, sorted(GROWTH_TYPES)))


def null_report(rows):
    """agents.md / NULL VISIBILITY — every null named before any arithmetic runs."""
    nulls = [r for r in rows if not r["actual_spend"].strip()]
    lines = ["NULL AUDIT — {} row(s) with no actual_spend, reported before computing:".format(len(nulls))]
    for row in nulls:
        lines.append("  {} · {} · {} — reason: {}".format(
            row["period"], row["ward"], row["category"],
            row["notes"].strip() or "no reason given in notes"))
    return "\n".join(lines), nulls


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


def compute_growth(rows, ward, category, growth_type):
    """
    Per-period growth for exactly one ward + category pair, using the growth
    type the caller explicitly asked for.

    Every source period produces exactly one output row, and every row states
    the arithmetic behind it. A null produces a NULL_FLAGGED row carrying its
    reason; a period whose comparison period is null produces a PRIOR_NULL row
    with no figure. The gap is never bridged, because a bridged figure is
    indistinguishable from a real one once it is in a table.
    """
    step = GROWTH_TYPES[growth_type]
    selected = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    by_period = {r["period"]: r for r in selected}

    results = []
    for row in selected:
        period = row["period"]
        raw = row["actual_spend"].strip()
        prior_period = shift_period(period, step)
        prior_row = by_period.get(prior_period)
        prior_raw = prior_row["actual_spend"].strip() if prior_row else ""

        record = {
            "ward": ward,
            "category": category,
            "period": period,
            "growth_type": growth_type,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": raw,
            "prior_period": prior_period,
            "prior_value": prior_raw,
            "growth_pct": "",
            "formula": "",
            "status": "",
            "note": "",
        }

        if not raw:
            record["status"] = "NULL_FLAGGED"
            record["formula"] = "not computed"
            record["note"] = row["notes"].strip() or "no reason given in notes"
        elif prior_row is None:
            record["status"] = "NO_PRIOR"
            record["formula"] = "not computed"
            record["note"] = "comparison period {} is not in the dataset".format(prior_period)
        elif not prior_raw:
            record["status"] = "PRIOR_NULL"
            record["formula"] = "not computed"
            record["note"] = (
                "comparison period {} has no actual_spend ({}) — growth not computed "
                "rather than bridged across the gap".format(
                    prior_period, prior_row["notes"].strip() or "no reason given")
            )
        else:
            value, prior = float(raw), float(prior_raw)
            record["growth_pct"] = round((value - prior) / prior * 100.0, 1)
            record["status"] = "COMPUTED"
            record["formula"] = "{} = (actual[{}] - actual[{}]) / actual[{}] * 100 = ({} - {}) / {} * 100".format(
                growth_type, period, prior_period, prior_period, value, prior, prior)

        results.append(record)
    return results


FIELDNAMES = ["ward", "category", "period", "growth_type", "budgeted_amount",
              "actual_spend", "prior_period", "prior_value", "growth_pct",
              "formula", "status", "note"]


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", help="Exactly one ward. Aggregate values are refused.")
    parser.add_argument("--category", help="Exactly one category. Aggregate values are refused.")
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY. Required — this tool will not guess.")
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

    try:
        check_formula(args.growth_type)
    except FormulaRefusal as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 4

    audit, _ = null_report(rows)
    print(audit)
    print("")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    flagged = [r for r in results if r["status"] != "COMPUTED"]
    print("{} rows written to {} ({} computed, {} flagged)".format(
        len(results), args.output, len(results) - len(flagged), len(flagged)))
    for row in flagged:
        print("  {} {} — {}".format(row["period"], row["status"], row["note"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

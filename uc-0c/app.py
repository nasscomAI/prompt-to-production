"""
UC-0C — Number That Looks Right

Per-ward, per-category growth on ward budget actuals.

The failure this file is built to prevent is not a wrong number. It is a
*plausible* number: one aggregate figure for the whole corporation, computed
with a formula nobody chose, over a series with five holes in it that were
skipped without comment. Every one of those three things produces output that
looks finished.

So: the grain is never collapsed, the formula is never assumed, and a gap is
always a row.

Run:
    python app.py \
      --input ../data/budget/ward_budget.csv \
      --ward "Ward 1" \
      --category "Roads" \
      --growth-type MoM \
      --output growth_output.csv

    # every ward and category, each computed separately — enumeration, not
    # aggregation:
    python app.py --input ../data/budget/ward_budget.csv \
      --ward ALL --category ALL --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

OUTPUT_FIELDS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "prior_period",
    "prior_actual_spend",
    "growth_type",
    "formula",
    "growth_pct",
    "status",
    "note",
]

SELECT_ALL = "ALL"


def _refuse(message: str):
    """
    Every refusal leaves by this door, so refusals are never a silent empty
    table. Exit is non-zero: a caller in a pipeline must be able to tell that
    no answer was given.
    """
    sys.exit("REFUSED: %s" % message)


def _normalise(value: str) -> str:
    """
    Fold the variations that come from typing a ward name by hand — the dataset
    uses an en dash, keyboards produce a hyphen.
    """
    folded = value.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", folded).strip().lower()


def _parse_amount(raw: str, column: str, row_label: str):
    """
    Blank becomes None. Blank never becomes 0.0.

    "we spent nothing" and "we do not know what was spent" are different facts,
    and collapsing them is exactly the silent-null failure this UC is about.
    """
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        _refuse("%s has non-numeric %s %r — refusing to coerce it." % (row_label, column, text))


def load_dataset(path: str) -> dict:
    """
    Read the CSV, validate the schema, and build the null report before any
    growth is computed.
    """
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                _refuse(
                    "%s is missing required column(s): %s. Refusing to guess the schema."
                    % (path, ", ".join(missing))
                )
            raw_rows = list(reader)
    except OSError as exc:
        sys.exit("Cannot read dataset %s: %s" % (path, exc))

    rows = []
    nulls = []
    for raw in raw_rows:
        label = "%s / %s / %s" % (raw["period"], raw["ward"], raw["category"])
        row = {
            "period": raw["period"].strip(),
            "ward": raw["ward"].strip(),
            "category": raw["category"].strip(),
            "budgeted_amount": _parse_amount(raw["budgeted_amount"], "budgeted_amount", label),
            "actual_spend": _parse_amount(raw["actual_spend"], "actual_spend", label),
            "notes": (raw["notes"] or "").strip(),
        }
        rows.append(row)
        if row["actual_spend"] is None:
            nulls.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    # Quoted from the notes column, not invented.
                    "reason": row["notes"] or "(no reason given in notes column)",
                }
            )

    return {
        "rows": rows,
        "wards": sorted({r["ward"] for r in rows}),
        "categories": sorted({r["category"] for r in rows}),
        "periods": sorted({r["period"] for r in rows}),
        "nulls": nulls,
    }


def resolve_selector(value: str, universe, label: str):
    """
    Turn a typed selector into exact dataset values, or refuse.

    Never falls back to a nearest match and never falls back to "everything".
    An ambiguous selector lists its candidates and stops.
    """
    if value == SELECT_ALL:
        return list(universe)

    wanted = _normalise(value)
    exact = [u for u in universe if _normalise(u) == wanted]
    if len(exact) == 1:
        return exact

    partial = [u for u in universe if wanted in _normalise(u)]
    if len(partial) == 1:
        return partial
    if len(partial) > 1:
        _refuse(
            "%s %r is ambiguous — it matches %s. Name one, or pass ALL to compute each "
            "separately." % (label, value, "; ".join(partial))
        )
    _refuse("Unknown %s %r. Valid values are: %s" % (label, value, "; ".join(universe)))


def _prior_period(period: str, growth_type: str) -> str:
    """The period this one is compared against."""
    year, month = (int(p) for p in period.split("-"))
    if growth_type == "MoM":
        return "%04d-%02d" % (year - 1, 12) if month == 1 else "%04d-%02d" % (year, month - 1)
    return "%04d-%02d" % (year - 1, month)


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str):
    """
    Return one row per period for this ward and category, in order.

    A period that cannot be computed still appears, carrying the reason. The
    row count is the period count — always.
    """
    series = {
        r["period"]: r
        for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    }
    if not series:
        _refuse(
            "No rows for ward %r and category %r. This combination does not exist in the "
            "dataset — returning an empty table would read as 'no growth'." % (ward, category)
        )

    results = []
    for period in sorted(series):
        row = series[period]
        prior_key = _prior_period(period, growth_type)
        prior = series.get(prior_key)

        current_value = row["actual_spend"]
        prior_value = prior["actual_spend"] if prior else None

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": "" if current_value is None else current_value,
            "prior_period": prior_key if prior else "",
            "prior_actual_spend": "" if prior_value is None else prior_value,
            "growth_type": growth_type,
            "formula": "",
            "growth_pct": "",
            "status": "",
            "note": "",
        }

        if prior is None:
            result["status"] = "NO_PRIOR_PERIOD"
            result["note"] = (
                "No %s baseline: %s is not in the dataset (coverage is %s to %s)."
                % (growth_type, prior_key, dataset["periods"][0], dataset["periods"][-1])
            )
        elif current_value is None:
            # The null's own period.
            result["status"] = "NULL_CURRENT"
            result["note"] = "actual_spend is null. Reason from notes: %s" % (
                row["notes"] or "(none given)"
            )
        elif prior_value is None:
            # The period *after* a null. Its baseline does not exist, so a
            # figure here would be computed against a number nobody recorded.
            result["status"] = "NULL_PRIOR"
            result["note"] = (
                "Baseline %s is null, so growth into %s cannot be computed. "
                "Reason from notes: %s" % (prior_key, period, prior["notes"] or "(none given)")
            )
        elif prior_value == 0:
            result["status"] = "UNDEFINED_ZERO_BASE"
            result["note"] = "Prior actual_spend is 0 — growth is undefined, not infinite."
        else:
            growth = (current_value - prior_value) / prior_value * 100
            result["status"] = "COMPUTED"
            # The operands are substituted, so any row can be rechecked from
            # that row alone without opening the source file.
            result["formula"] = "(%g - %g) / %g * 100" % (
                current_value,
                prior_value,
                prior_value,
            )
            result["growth_pct"] = "%.1f" % growth

        results.append(result)

    return results


def print_null_report(dataset: dict, out=sys.stdout):
    """
    Printed before the first growth figure — that ordering is the enforcement
    rule, not a formatting preference. A null report appended underneath a
    finished table is read after the reader has already believed the numbers.
    """
    print("NULL REPORT — read before the numbers", file=out)
    print("  %d null actual_spend value(s) in %d rows" % (len(dataset["nulls"]), len(dataset["rows"])), file=out)
    if not dataset["nulls"]:
        print("  none", file=out)
    for null in dataset["nulls"]:
        print(
            "  %s  %-24s %-26s %s"
            % (null["period"], null["ward"], null["category"], null["reason"]),
            file=out,
        )
    print("", file=out)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator",
        epilog="Growth is computed per ward per category. Aggregation across wards is refused.",
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    parser.add_argument("--ward", help='Ward name, or ALL to compute each ward separately')
    parser.add_argument("--category", help='Category name, or ALL to compute each separately')
    # Deliberately NOT required=True. argparse would exit with a usage error;
    # this UC calls for an explicit refusal that names the choice being ducked.
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY — never defaulted")
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Request a combined figure across wards/categories (this is refused by design)",
    )
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    # Rule 2: the gaps are reported before anything is computed.
    print_null_report(dataset)

    if args.aggregate:
        _refuse(
            "Aggregation across wards or categories is not supported. A single combined growth "
            "figure hides which ward moved and is not actionable by any ward officer. Use "
            "--ward ALL --category ALL to compute every combination separately."
        )

    if not args.growth_type:
        _refuse(
            "--growth-type was not specified. MoM and YoY answer different questions and this "
            "system does not choose for you. Pass --growth-type MoM or --growth-type YoY."
        )

    growth_type = args.growth_type.strip()
    if growth_type.upper() not in {"MOM", "YOY"}:
        _refuse("Unknown --growth-type %r. Valid values are MoM and YoY." % args.growth_type)
    growth_type = "MoM" if growth_type.upper() == "MOM" else "YoY"

    if not args.ward:
        _refuse(
            "--ward was not specified. This system does not default to all wards, because a "
            "figure spanning every ward is an aggregate. Pass a ward name, or --ward ALL to "
            "compute each ward separately."
        )
    if not args.category:
        _refuse(
            "--category was not specified. Pass a category name, or --category ALL to compute "
            "each category separately."
        )

    wards = resolve_selector(args.ward, dataset["wards"], "ward")
    categories = resolve_selector(args.category, dataset["categories"], "category")

    rows = []
    for ward in wards:
        for category in categories:
            rows.extend(compute_growth(dataset, ward, category, growth_type))

    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    tally = {}
    for row in rows:
        tally[row["status"]] = tally.get(row["status"], 0) + 1

    expected = len(wards) * len(categories) * len(dataset["periods"])
    print("Done. Growth table written to %s" % args.output)
    print("  grain             : per ward per category (never aggregated)")
    print("  wards             : %d" % len(wards))
    print("  categories        : %d" % len(categories))
    print("  growth type       : %s" % growth_type)
    print("  rows written      : %d (expected %d)" % (len(rows), expected))
    for status, count in sorted(tally.items()):
        print("  %-20s: %d" % (status, count))

    if len(rows) != expected:
        sys.exit("Row count mismatch — a period was dropped from the table.")


if __name__ == "__main__":
    main()

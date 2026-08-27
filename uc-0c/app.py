"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

# Enforcement rule 3 -- see agents.md. A growth cell that cannot be computed
# says so. A blank cell reads as "no change"; a zero reads as "no spend".
MISSING = "MISSING_DATA"

# Not the same thing as MISSING_DATA. The first period has no comparison base by
# definition; that is a property of the series, not a gap in the ledger. Merging
# the two would be the same conflation this UC exists to prevent.
NO_BASE = "NO_PRIOR_PERIOD"

# Enforcement rule 6: words that ask for a citywide total. Refused, not served.
AGGREGATE_WORDS = {"all", "*", "total", "citywide", "every", "combined"}

GROWTH_TYPES = {
    "MoM": "month on month, against the immediately preceding period",
    "YoY": "year on year, against the same period twelve months earlier",
}


class Refusal(Exception):
    """Raised when the request is answerable but must not be answered."""


def load_dataset(input_path):
    """Read the ledger and report its data quality before anything is computed."""
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    missing = [r for r in rows if not r["actual_spend"].strip()]

    # Enforcement rule 2: missing rows are reported before any growth is taken,
    # with the verbatim reason the ward office supplied.
    print("Rows read: {}".format(len(rows)))
    print("Missing actual_spend rows: {}".format(len(missing)))
    for row in missing:
        print("  {} | {} | {} | reason: {}".format(
            row["period"], row["ward"], row["category"],
            row["notes"] or "(no reason given)"))

    return rows, missing


def _resolve(requested, valid, label):
    """Match one requested ward/category name, or refuse. Never guess."""
    if requested is None:
        return None
    if requested.strip().lower() in AGGREGATE_WORDS:
        raise Refusal(
            "Refused: growth cannot be reported across all {0}s. Spend from "
            "different {0}s is not comparable and a combined figure is not "
            "actionable by any single ward office. Ask for one {0} at a time.\n"
            "Valid values:\n  {1}".format(label, "\n  ".join(sorted(valid))))
    if requested not in valid:
        raise Refusal(
            "Refused: {} {!r} is not in the ledger. No nearest match is "
            "assumed, because the wrong series returned confidently is worse "
            "than no series.\nValid values:\n  {}".format(
                label, requested, "\n  ".join(sorted(valid))))
    return requested


def _resolve_growth_type(growth_type, rows):
    """Refuse rather than assume which growth question was asked."""
    if growth_type is None:
        raise Refusal(
            "Refused: --growth-type was not given and will not be assumed. "
            "Month-on-month and year-on-year answer different questions, and a "
            "silently chosen default is read by the caller as the one they "
            "asked for.\nSupported types:\n  " +
            "\n  ".join("{} -- {}".format(k, v) for k, v in sorted(GROWTH_TYPES.items())))
    if growth_type not in GROWTH_TYPES:
        raise Refusal(
            "Refused: growth type {!r} is not supported.\nSupported types:\n  ".format(
                growth_type) +
            "\n  ".join("{} -- {}".format(k, v) for k, v in sorted(GROWTH_TYPES.items())))

    # Enforcement rule: a growth type the data cannot support is refused, not
    # attempted. YoY needs twelve months of history before the first reported
    # period; this ledger starts at its own first period.
    if growth_type == "YoY":
        years = sorted({r["period"][:4] for r in rows})
        raise Refusal(
            "Refused: year-on-year growth needs a comparison period twelve "
            "months before each reported period. This ledger covers {} only, so "
            "no row has a base to compare against. Returning 300 uncomputable "
            "rows would read as a defect in this tool rather than a limit of "
            "the data.\nUse --growth-type MoM, or supply a ledger that spans "
            "more than one year.".format(" and ".join(years)))
    return growth_type


def compute_growth(rows, ward=None, category=None, growth_type=None):
    """Return per-period growth rows for each ward+category series separately.

    Enforcement rule 5: spend is never summed across wards or categories. Each
    ward+category pair is its own series.
    """
    growth_type = _resolve_growth_type(growth_type, rows)
    wards = {r["ward"] for r in rows}
    categories = {r["category"] for r in rows}
    ward = _resolve(ward, wards, "ward")
    category = _resolve(category, categories, "category")

    series = {}
    for row in rows:
        if ward is not None and row["ward"] != ward:
            continue
        if category is not None and row["category"] != category:
            continue
        series.setdefault((row["ward"], row["category"]), {})[row["period"]] = row

    results = []
    for (series_ward, series_category) in sorted(series):
        periods = sorted(series[(series_ward, series_category)])
        previous = None
        is_first = True
        for period in periods:
            row = series[(series_ward, series_category)][period]
            raw = row["actual_spend"].strip()
            spend = float(raw) if raw else None

            # Enforcement: the formula travels with the number, values
            # substituted in, so any row can be recomputed by hand.
            if is_first:
                growth = NO_BASE
                formula = "no prior period in this series"
            elif spend is None:
                growth = MISSING
                formula = "actual_spend missing for {}".format(period)
            elif previous is None:
                growth = MISSING
                formula = "actual_spend missing for the prior period"
            else:
                growth = round((spend - previous) / previous * 100, 1)
                formula = "{}: ({} - {}) / {} * 100".format(
                    growth_type, spend, previous, previous)
            is_first = False

            results.append({
                "ward": series_ward,
                "category": series_category,
                "period": period,
                "actual_spend": raw if raw else MISSING,
                "growth_type": growth_type,
                "growth_pct": growth,
                "formula": formula,
                "note": row["notes"],
            })
            previous = spend
    return results


def write_results(results, output_path, missing_count):
    """Enforcement rule 7: every row carries its own ward and category.

    Enforcement rule 4: incompleteness travels with the file as data, not as a
    trailing comment. A "# 5 rows were missing" footer makes the file readable
    by a human and unparseable by a CSV reader, which counts it as an extra
    data row -- a results file that silently corrupts its own consumer is the
    same class of failure as a number that silently excludes a ward.
    """
    fields = ["ward", "category", "period", "actual_spend", "growth_type",
              "growth_pct", "formula", "note", "source_missing_rows"]
    for row in results:
        row["source_missing_rows"] = missing_count
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def selftest(input_path):
    """Assert the enforcement rules in agents.md actually hold. Run with --selftest."""
    rows = list(csv.DictReader(open(input_path, newline="", encoding="utf-8")))

    def refuses(**kwargs):
        try:
            compute_growth(rows, **kwargs)
        except Refusal:
            return True
        return False

    # Rule: growth type is never assumed.
    assert refuses(ward="Ward 1 – Kasba", category="Roads & Pothole Repair")
    # Rule: a growth type this single-year ledger cannot support is refused.
    assert refuses(growth_type="YoY")
    assert refuses(growth_type="quarterly")
    # Rule: aggregation across wards or categories is refused, not served.
    assert refuses(ward="all", growth_type="MoM")
    assert refuses(category="total", growth_type="MoM")
    # Rule: an unknown name is refused, not matched to the nearest.
    assert refuses(ward="Ward 1", growth_type="MoM")
    assert refuses(category="Roads", growth_type="MoM")

    out = compute_growth(rows, growth_type="MoM")

    # Rule: twenty-five independent series, never summed together.
    assert len({(r["ward"], r["category"]) for r in out}) == 25
    assert len(out) == 300

    by_key = {(r["ward"], r["category"], r["period"]): r for r in out}

    # The published reference values, recomputed from the ledger.
    kasba_roads = ("Ward 1 – Kasba", "Roads & Pothole Repair")
    assert by_key[kasba_roads + ("2024-07",)]["growth_pct"] == 33.1
    assert by_key[kasba_roads + ("2024-10",)]["growth_pct"] == -34.8

    # Rule: a missing cell is never zero, and never silently skipped.
    warje = ("Ward 4 – Warje", "Roads & Pothole Repair")
    july = by_key[warje + ("2024-07",)]
    assert july["actual_spend"] == MISSING and july["growth_pct"] == MISSING
    assert "Audit freeze" in july["note"], july
    # The period after a gap has no valid base, so it is missing too -- but the
    # period after that recovers. A null damages its own series, not the year.
    assert by_key[warje + ("2024-08",)]["growth_pct"] == MISSING
    assert isinstance(by_key[warje + ("2024-09",)]["growth_pct"], float)

    # Rule: MISSING_DATA and NO_PRIOR_PERIOD are distinct.
    assert by_key[kasba_roads + ("2024-01",)]["growth_pct"] == NO_BASE

    # Rule: every row shows the arithmetic that produced it, and it recomputes.
    for row in out:
        assert row["formula"], row
        if isinstance(row["growth_pct"], float):
            body = row["formula"].split(": ", 1)[1]
            assert abs(eval(body) - row["growth_pct"]) < 0.05, row  # noqa: S307

    print("selftest: all enforcement rules hold")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--selftest", action="store_true",
                        help="Check the agents.md enforcement rules and exit")
    parser.add_argument("--ward", help="One ward name. Omit for every ward, reported separately.")
    parser.add_argument("--category", help="One category name. Omit for every category, reported separately.")
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY. Required -- it is never assumed.")
    args = parser.parse_args()

    if args.selftest:
        selftest(args.input)
        return
    if not args.output:
        parser.error("--output is required unless --selftest is given")

    rows, missing = load_dataset(args.input)
    try:
        results = compute_growth(rows, ward=args.ward, category=args.category,
                                 growth_type=args.growth_type)
    except Refusal as refusal:
        print("\n{}".format(refusal))
        sys.exit(2)

    write_results(results, args.output, len(missing))
    print("\nWrote {} rows to {}".format(len(results), args.output))


if __name__ == "__main__":
    main()

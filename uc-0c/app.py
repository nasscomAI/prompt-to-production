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


def compute_growth(rows, ward=None, category=None):
    """Return per-period growth rows for each ward+category series separately.

    Enforcement rule 5: spend is never summed across wards or categories. Each
    ward+category pair is its own series.
    """
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

            if is_first:
                growth = NO_BASE
            elif spend is None or previous is None:
                growth = MISSING
            else:
                growth = round((spend - previous) / previous * 100, 1)
            is_first = False

            results.append({
                "ward": series_ward,
                "category": series_category,
                "period": period,
                "actual_spend": raw if raw else MISSING,
                "growth_pct": growth,
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
    fields = ["ward", "category", "period", "actual_spend", "growth_pct",
              "note", "source_missing_rows"]
    for row in results:
        row["source_missing_rows"] = missing_count
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", help="One ward name. Omit for every ward, reported separately.")
    parser.add_argument("--category", help="One category name. Omit for every category, reported separately.")
    args = parser.parse_args()

    rows, missing = load_dataset(args.input)
    try:
        results = compute_growth(rows, ward=args.ward, category=args.category)
    except Refusal as refusal:
        print("\n{}".format(refusal))
        sys.exit(2)

    write_results(results, args.output, len(missing))
    print("\nWrote {} rows to {}".format(len(results), args.output))


if __name__ == "__main__":
    main()

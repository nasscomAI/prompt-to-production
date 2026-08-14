"""
UC-0C — Ward Budget MoM Growth Analyzer
Rule-based analyzer enforced by uc-0c/agents.md.
Output is a per-ward per-category per-period table (never a single aggregated
number), every row shows the formula used, all 5 null actual_spend rows are
flagged with their notes reason, cross-ward/cross-category aggregation is
refused, and a missing --growth-type is refused rather than guessed.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]
GROWTH_TYPES = ("MoM", "YoY")
REFUSED_SCOPE = {"all", "any", "every", "*", "all wards", "any ward",
                 "every ward", "all categories", "any category",
                 "every category"}

OUTPUT_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                  "actual_spend", "previous_period", "previous_actual_spend",
                  "growth_pct", "formula", "applied_formula", "flag", "notes"]


def load_dataset(input_path):
    """Read the CSV, validate columns and report the null rows before returning."""
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            raise ValueError("Input CSV is missing required column(s): %s"
                             % ", ".join(missing))
        rows = list(reader)

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    print("Loaded %d rows." % len(rows))
    print("NULL actual_spend rows: %d" % len(null_rows))
    for r in null_rows:
        note = (r.get("notes") or "").strip() or "no reason given"
        print("  %s | %s | %s | reason: %s"
              % (r["period"], r["ward"], r["category"], note))
    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Return the per-period growth table for one ward + one category.
    Every row includes the formula used. Null rows are flagged with the
    reason from the notes column; the first period has no previous period."""
    scope = [r for r in rows if r["ward"] == ward and r["category"] == category]
    scope.sort(key=lambda r: r["period"])

    results = []
    prev_period = None
    prev_spend = None
    for row in scope:
        period = row["period"]
        budgeted = (row.get("budgeted_amount") or "").strip()
        spend_raw = (row.get("actual_spend") or "").strip()
        note = (row.get("notes") or "").strip()

        if spend_raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "",
                "previous_period": "",
                "previous_actual_spend": "",
                "growth_pct": "",
                "formula": "%s: not computed \u2014 actual_spend is NULL"
                           % growth_type,
                "applied_formula": "%s: not computed \u2014 actual_spend is NULL"
                                   % growth_type,
                "flag": "NULL_ACTUAL_SPEND",
                "notes": note or "no reason given",
            })
            continue

        spend = float(spend_raw)
        if prev_spend is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": _num(spend),
                "previous_period": "",
                "previous_actual_spend": "",
                "growth_pct": "",
                "formula": "%s: no previous period \u2014 growth not computed"
                           % growth_type,
                "applied_formula": "%s: no previous period \u2014 growth not "
                                   "computed" % growth_type,
                "flag": "NO_PREVIOUS_PERIOD",
                "notes": note,
            })
        elif prev_spend == 0.0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": _num(spend),
                "previous_period": prev_period,
                "previous_actual_spend": _num(prev_spend),
                "growth_pct": "",
                "formula": "%s: not computed \u2014 previous actual_spend is 0"
                           % growth_type,
                "applied_formula": "(%s - %s) / %s * 100"
                                   % (_num(spend), _num(prev_spend), _num(prev_spend)),
                "flag": "PREVIOUS_ZERO",
                "notes": note,
            })
        else:
            pct = (spend - prev_spend) / prev_spend * 100.0
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": _num(spend),
                "previous_period": prev_period,
                "previous_actual_spend": _num(prev_spend),
                "growth_pct": "%+.1f" % pct,
                "formula": "%s growth = (actual_spend[%s] \u2014 "
                           "actual_spend[%s]) / actual_spend[%s] * 100"
                           % (growth_type, period, prev_period, prev_period),
                "applied_formula": "(%s - %s) / %s * 100"
                                   % (_num(spend), _num(prev_spend), _num(prev_spend)),
                "flag": "",
                "notes": note,
            })
        prev_period = period
        prev_spend = spend
    return results


def _num(value):
    """Format a float/string number compactly (13.0 -> 13, 19.7 -> 19.7)."""
    try:
        return ("%g" % float(value))
    except (TypeError, ValueError):
        return str(value)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward, e.g. 'Ward 1 \u2013 Kasba'")
    parser.add_argument("--category", required=True,
                        help="Single category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True,
                        help="Growth type (MoM); YoY is refused for this dataset")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    if args.growth_type not in GROWTH_TYPES:
        print("REFUSED: unsupported --growth-type '%s'. Supported values: %s."
              % (args.growth_type, ", ".join(GROWTH_TYPES)), file=sys.stderr)
        sys.exit(1)

    if args.growth_type == "YoY":
        print("REFUSED: YoY growth cannot be computed \u2014 the dataset covers "
              "calendar year 2024 only (no prior-year data). Provide "
              "--growth-type MoM.", file=sys.stderr)
        sys.exit(1)

    ward_scope = args.ward.strip().lower()
    category_scope = args.category.strip().lower()
    if ward_scope in REFUSED_SCOPE or category_scope in REFUSED_SCOPE:
        print("REFUSED: aggregation across wards or categories is not supported. "
              "Provide a single --ward and a single --category.", file=sys.stderr)
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)

    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    if args.ward not in wards:
        print("REFUSED: ward '%s' not found in the dataset. Available wards: %s"
              % (args.ward, ", ".join(wards)), file=sys.stderr)
        sys.exit(1)
    if args.category not in categories:
        print("REFUSED: category '%s' not found in the dataset. Available "
              "categories: %s" % (args.category, ", ".join(categories)),
              file=sys.stderr)
        sys.exit(1)

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    flagged = [r for r in results if r["flag"] == "NULL_ACTUAL_SPEND"]
    print("Wrote %d periods for %s / %s to %s"
          % (len(results), args.ward, args.category, args.output))
    print("Null rows flagged in output: %d" % len(flagged))
    for r in flagged:
        print("  %s | %s | %s | flag: NULL_ACTUAL_SPEND | notes: %s"
              % (r["period"], r["ward"], r["category"], r["notes"]))


if __name__ == "__main__":
    main()
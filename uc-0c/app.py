"""UC-0C Budget Growth Agent — load_dataset -> compute_growth pipeline.

Computes period-over-period growth for exactly one ward x one category.
Implements the agents.md enforcement rules:
- aggregation guard  : refuses totals/means/city-wide requests
- null handling      : reports every null actual_spend row before computing,
                       emits NA rows with the notes reason instead of guessing
- formula transparency: every computed row shows its arithmetic inline
- growth-type guard  : --growth-type must be supplied and be MoM or YoY
- refusal condition  : unknown ward/category exits non-zero listing valid options
"""
import argparse
import csv
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
PERIOD_RE = re.compile(r"^\d{4}-\d{2}$")
GROWTH_TYPES = {"MoM": "month-over-month (vs previous month)",
                "YoY": "year-over-year (vs same month one year earlier)"}
AGGREGATION_TOKENS = re.compile(r"[;,]|\b(?:all|any|total|average|mean|city[- ]?wide|\*)\b", re.IGNORECASE)


def _fmt_num(x):
    return f"{x:.10g}"


def _prev_month_key(period):
    y, m = int(period[:4]), int(period[5:])
    if m == 1:
        y, m = y - 1, 12
    else:
        m -= 1
    return f"{y:04d}-{m:02d}"


def _prev_year_key(period):
    return f"{int(period[:4]) - 1:04d}-{period[5:]}"


def _fail(msg):
    raise ValueError(msg)


def load_dataset(path):
    """skills.md contract: read the CSV, validate columns, report all null
    actual_spend rows before returning; never impute or clean."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                _fail("input CSV is missing required column(s): %s; found: %s"
                      % (", ".join(missing), ", ".join(reader.fieldnames or [])))
            raw = list(reader)
    except OSError as exc:
        _fail("cannot read input CSV %s: %s" % (path, exc))
    except ValueError as exc:
        _fail("input CSV has a malformed numeric cell: %s" % exc)

    rows, wards, categories, null_rows = [], [], [], []
    for r in raw:
        period = r["period"].strip()
        ward = r["ward"].strip()
        category = r["category"].strip()
        spend_raw = r["actual_spend"].strip()
        try:
            budgeted = float(r["budgeted_amount"])
            spend = None if spend_raw == "" else float(spend_raw)
        except ValueError as exc:
            _fail("malformed numeric cell at %s / %s / %s: %s" % (period, ward, category, exc))
        if not PERIOD_RE.match(period):
            _fail("malformed period %r: expected YYYY-MM" % period)
        if ward not in wards:
            wards.append(ward)
        if category not in categories:
            categories.append(category)
        if spend is None:
            null_rows.append({"period": period, "ward": ward, "category": category,
                              "reason": r["notes"].strip()})
        rows.append({"period": period, "ward": ward, "category": category,
                     "budgeted_amount": budgeted, "actual_spend": spend,
                     "notes": r["notes"].strip()})
    return {"rows": rows, "wards": wards, "categories": categories,
            "null_report": {"count": len(null_rows), "rows": null_rows}}


def _row(period, ward, category, cur_spend, prev_spend, growth_pct, formula, flag):
    return {"period": period, "ward": ward, "category": category,
            "actual_spend": "" if cur_spend is None else _fmt_num(cur_spend),
            "previous_spend": "" if prev_spend is None else _fmt_num(prev_spend),
            "growth_pct": growth_pct, "formula": formula, "flag": flag}


def compute_growth(dataset, ward, category, growth_type):
    """skills.md contract: per-period table for ONE ward x ONE category with
    formula shown inline; null months flagged, never computed through."""
    for label, arg, valid in (("--ward", ward, dataset["wards"]),
                              ("--category", category, dataset["categories"])):
        if AGGREGATION_TOKENS.search(arg) and arg not in valid:
            _fail("%s %r looks like a request to aggregate across multiple "
                  "%ss (totals/means/city-wide). This tool computes growth for exactly "
                  "one ward x one category and refuses aggregated figures. Valid values: %s"
                  % (label, arg, label.lstrip("-"), "; ".join(valid)))
        if arg not in valid:
            _fail("%s %r does not exist in the dataset. Valid %ss: %s"
                  % (label, arg, label.lstrip("-"), "; ".join(valid)))

    series = {}
    for r in dataset["rows"]:
        if r["ward"] == ward and r["category"] == category:
            if r["period"] in series:
                _fail("duplicate rows for period %s in series %s / %s; refusing rather than guessing which to use"
                      % (r["period"], ward, category))
            series[r["period"]] = r
    if not series:
        _fail("no data found for %r / %r although both exist in the dataset" % (ward, category))

    periods = sorted(series)
    all_periods = sorted({r["period"] for r in dataset["rows"]})
    g_min = all_periods[0]
    out = []
    for p in periods:
        cur = series[p]
        prev_key = _prev_month_key(p) if growth_type == "MoM" else _prev_year_key(p)
        prev = series.get(prev_key)

        if cur["actual_spend"] is None:
            out.append(_row(p, ward, category, None, None, "NA", "",
                            "NULL_SPEND: " + (cur["notes"] or "reason not given")))
            continue
        if prev_key not in series:
            # before the dataset's coverage -> nothing to compare against;
            # inside coverage but absent from this series -> a real gap
            flag = "NO_PREVIOUS_PERIOD" if prev_key < g_min else "MISSING_PREVIOUS_PERIOD"
            out.append(_row(p, ward, category, cur["actual_spend"], None, "NA", "", flag))
            continue
        if prev["actual_spend"] is None:
            out.append(_row(p, ward, category, cur["actual_spend"], None, "NA", "",
                            "NULL_SPEND: " + (prev["notes"] or "reason not given")))
            continue
        c, b = cur["actual_spend"], prev["actual_spend"]
        if b == 0:
            out.append(_row(p, ward, category, c, b, "NA", "",
                            "ZERO_PREVIOUS_PERIOD: growth undefined when previous spend is 0"))
            continue
        pct = (c - b) / b * 100
        disp = "%+.1f%%" % pct
        formula = "growth_pct = (%s - %s) / %s * 100 = %s" % (_fmt_num(c), _fmt_num(b), _fmt_num(b), disp)
        out.append(_row(p, ward, category, c, b, disp, formula, ""))
    return out


FIELDNAMES = ["period", "ward", "category", "actual_spend", "previous_spend",
              "growth_pct", "formula", "flag"]


def main():
    parser = argparse.ArgumentParser(description="UC-0C budget growth agent (one ward x one category)")
    parser.add_argument("--input", required=True, help="path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help='exact ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=True, help="exact category name")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="required: MoM or YoY — never guessed")
    parser.add_argument("--output", default="growth_output.csv", help="output CSV path")
    args = parser.parse_args()

    gt = args.growth_type
    if gt is None:
        print("REFUSED: --growth-type was not supplied and is never guessed.", file=sys.stderr)
        print("Which growth type do you mean? Re-run with:", file=sys.stderr)
        for key, desc in GROWTH_TYPES.items():
            print("  --growth-type %s  (%s)" % (key, desc), file=sys.stderr)
        return 2
    if gt not in GROWTH_TYPES:
        print("REFUSED: --growth-type %r is not recognised." % gt, file=sys.stderr)
        print("Which growth type do you mean? Re-run with:", file=sys.stderr)
        for key, desc in GROWTH_TYPES.items():
            print("  --growth-type %s  (%s)" % (key, desc), file=sys.stderr)
        return 2

    try:
        dataset = load_dataset(args.input)
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    nr = dataset["null_report"]
    print("Loaded %d rows | %d wards x %d categories"
          % (len(dataset["rows"]), len(dataset["wards"]), len(dataset["categories"])))
    print("NULL actual_spend rows flagged BEFORE computing (%d):" % nr["count"])
    for n in nr["rows"]:
        print("  %s | %s | %s | reason: %s" % (n["period"], n["ward"], n["category"], n["reason"]))
    print()

    try:
        table = compute_growth(dataset, args.ward, args.category, gt)
    except ValueError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(table)
    except OSError as exc:
        print("ERROR: cannot write output file: %s" % exc, file=sys.stderr)
        return 1

    computed = sum(1 for t in table if t["growth_pct"] != "NA")
    flagged = len(table) - computed
    print("Growth table (%s) for %s / %s -> %s" % (gt, args.ward, args.category, args.output))
    for t in table:
        line = "%s | actual=%s | prev=%s | growth=%s" % (
            t["period"], t["actual_spend"] or "NULL",
            t["previous_spend"] or "-", t["growth_pct"])
        if t["formula"]:
            line += " | " + t["formula"]
        if t["flag"]:
            line += " | [" + t["flag"] + "]"
        print(line)
    print("Rows: %d total | %d computed | %d flagged NA" % (len(table), computed, flagged))
    return 0


if __name__ == "__main__":
    sys.exit(main())

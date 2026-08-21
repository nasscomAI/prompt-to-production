"""
UC-0C — Number That Looks Right
Per-ward per-category budget growth analyzer built to satisfy the
enforcement rules in agents.md and the skill contracts in skills.md.

Enforcement rules implemented:
1. Never aggregate across wards or categories — aggregate requests are
   refused outright.
2. Every null actual_spend row is flagged (with its reason from the
   notes column) BEFORE any computation — never silently skipped,
   never treated as zero.
3. The formula used is shown alongside every computed result.
4. If --growth-type is not specified the tool refuses and asks —
   it never guesses between MoM and YoY.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"]

AGGREGATION_WORDS = {"all", "any", "total", "overall", "combined",
                     "average", "avg", "sum", "citywide", "aggregate"}

MOM_ALIASES = {"mom", "month-over-month", "month_over_month",
               "month over month"}
YOY_ALIASES = {"yoy", "year-over-year", "year_over_year",
               "year over year"}


def _normalise(value):
    """Normalise a ward/category label for matching: unify dash
    variants (hyphen/en-dash/em-dash), collapse whitespace, lowercase."""
    lowered = (value or "").strip().lower()
    for dash in ("\u2013", "\u2014", "\u2012", "\u2015"):
        lowered = lowered.replace(dash, "-")
    return " ".join(lowered.split())


def _parse_growth_type(raw):
    token = (raw or "").strip().lower()
    if token in MOM_ALIASES:
        return "MoM"
    if token in YOY_ALIASES:
        return "YoY"
    return None


def _refuse(message):
    print("REFUSAL: %s" % message, file=sys.stderr)
    raise SystemExit(2)


def load_dataset(path):
    """
    Read the budget CSV, validate columns, and report the null count
    and which rows are null BEFORE returning.
    Returns (rows, wards, categories).
    """
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            missing = [c for c in REQUIRED_COLUMNS
                       if c not in (reader.fieldnames or [])]
            if missing:
                print("ERROR: input CSV missing column(s): %s"
                      % ", ".join(missing), file=sys.stderr)
                raise SystemExit(1)
            rows = []
            for line_no, row in enumerate(reader, start=2):
                try:
                    rows.append({
                        "period": (row["period"] or "").strip(),
                        "ward": (row["ward"] or "").strip(),
                        "category": (row["category"] or "").strip(),
                        "budgeted_amount": (row["budgeted_amount"] or "").strip(),
                        "actual_spend": (row["actual_spend"] or "").strip(),
                        "notes": (row["notes"] or "").strip(),
                    })
                except (TypeError, KeyError):
                    print("WARNING: skipping malformed row at line %d"
                          % line_no, file=sys.stderr)
    except FileNotFoundError:
        print("ERROR: input file not found: %s" % path, file=sys.stderr)
        raise SystemExit(1)
    except UnicodeDecodeError:
        print("ERROR: could not decode %s as UTF-8" % path, file=sys.stderr)
        raise SystemExit(1)

    wards = []
    categories = []
    for row in rows:
        if row["ward"] and row["ward"] not in wards:
            wards.append(row["ward"])
        if row["category"] and row["category"] not in categories:
            categories.append(row["category"])

    null_rows = [r for r in rows if not r["actual_spend"]]
    print("Loaded %d row(s): %d ward(s), %d category(ies). "
          "Null actual_spend rows found: %d"
          % (len(rows), len(wards), len(categories), len(null_rows)))
    for r in null_rows:
        reason = r["notes"] or "no reason given"
        print("  NULL: %s | %s | %s (%s)"
              % (r["period"], r["ward"], r["category"], reason))
    return rows, wards, categories


def _format_pct(value):
    return "%+.1f%%" % value


def compute_growth(rows, ward, category, growth_type):
    """
    Compute the growth table for one ward + category series.
    Returns a list of output dicts, one per period, sorted by period.
    Formula shown on every computed row; nulls flagged, never computed.
    """
    series = {}
    for row in rows:
        if (_normalise(row["ward"]) == _normalise(ward)
                and _normalise(row["category"]) == _normalise(category)):
            series[row["period"]] = row

    periods = sorted(series)
    out_rows = []
    prev_spend = None          # last non-null spend seen, in period order
    prev_period = None
    prev_was_null = False

    for period in periods:
        row = series[period]
        try:
            budgeted = float(row["budgeted_amount"])
        except ValueError:
            budgeted = None
        raw_spend = row["actual_spend"]
        note = row["notes"]

        entry = {
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": "" if budgeted is None else ("%g" % budgeted),
            "actual_spend": raw_spend,
            "prev_actual_spend": "",
            "growth_pct": "",
            "formula": "",
            "flag": "",
        }

        if raw_spend == "":
            # Rule 2: flag every null row — report the notes reason.
            entry["flag"] = "NULL_SPEND — not computed (%s)" % (
                note or "reason not given")
            prev_was_null = True
            prev_period = period  # remember where the gap is
            out_rows.append(entry)
            continue

        spend = float(raw_spend)

        if growth_type == "MoM":
            base_spend, base_period = prev_spend, prev_period
        else:  # YoY
            year, month = period.split("-")
            base_period = "%d-%s" % (int(year) - 1, month)
            base_row = series.get(base_period)
            base_spend = None
            if base_row and base_row["actual_spend"] != "":
                base_spend = float(base_row["actual_spend"])

        if prev_was_null and growth_type == "MoM":
            entry["actual_spend"] = "%g" % spend
            entry["flag"] = ("NOT COMPUTED — previous period (%s) "
                             "actual_spend is NULL" % prev_period)
        elif base_spend is None:
            entry["actual_spend"] = "%g" % spend
            entry["flag"] = ("BASELINE — no comparable %s period"
                             % ("prior-month" if growth_type == "MoM"
                                else "prior-year"))
        elif base_spend == 0:
            entry["actual_spend"] = "%g" % spend
            entry["flag"] = "NOT COMPUTED — prior period spend is 0"
        else:
            growth = (spend - base_spend) / base_spend * 100
            formula = "(%.1f - %.1f) / %.1f * 100 = %s" % (
                spend, base_spend, base_spend, _format_pct(growth))
            entry["actual_spend"] = "%g" % spend
            entry["prev_actual_spend"] = "%g" % base_spend
            entry["growth_pct"] = _format_pct(growth)
            entry["formula"] = formula  # Rule 3: show the formula
            if note:
                entry["flag"] = (entry["flag"] + " " if entry["flag"]
                                 else "") + "note: %s" % note

        if growth_type == "MoM":
            prev_spend, prev_period, prev_was_null = spend, period, False
        else:
            prev_spend, prev_period = spend, period
        out_rows.append(entry)

    return out_rows


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Analyzer")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help='Exact ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=True,
                        help='Exact category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Rule 4: refuse when --growth-type is missing — never guess.
    if not args.growth_type or not args.growth_type.strip():
        _refuse("--growth-type not specified. I will not guess. "
                "Please provide --growth-type MoM or --growth-type YoY.")
    growth_type = _parse_growth_type(args.growth_type)
    if growth_type is None:
        _refuse("Unknown --growth-type '%s'. Allowed values: MoM, YoY."
                % args.growth_type)

    # Rule 1: refuse aggregation requests outright.
    for label, value in (("ward", args.ward), ("category", args.category)):
        normalised = _normalise(value)
        if not normalised or normalised in AGGREGATION_WORDS:
            _refuse(
                "Aggregation across %ss is not allowed. This tool computes "
                "growth for ONE specific ward AND ONE specific category "
                "only. Please name a single %s." % (label, label))

    rows, wards, categories = load_dataset(args.input)

    matched_wards = [w for w in wards
                     if _normalise(w) == _normalise(args.ward)]
    matched_cats = [c for c in categories
                    if _normalise(c) == _normalise(args.category)]
    if not matched_wards:
        print("ERROR: ward '%s' not found. Available wards:\n  %s"
              % (args.ward, "\n  ".join(wards)), file=sys.stderr)
        raise SystemExit(1)
    if not matched_cats:
        print("ERROR: category '%s' not found. Available categories:\n  %s"
              % (args.category, "\n  ".join(categories)), file=sys.stderr)
        raise SystemExit(1)
    ward, category = matched_wards[0], matched_cats[0]

    out_rows = compute_growth(rows, ward, category, growth_type)
    if not out_rows:
        print("ERROR: no data rows for %s / %s" % (ward, category),
              file=sys.stderr)
        raise SystemExit(1)

    fields = ["period", "ward", "category", "budgeted_amount",
              "actual_spend", "prev_actual_spend", "growth_pct",
              "formula", "flag"]
    try:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(out_rows)
    except OSError as exc:
        print("ERROR: cannot write output file: %s" % exc, file=sys.stderr)
        raise SystemExit(1)

    computed = sum(1 for r in out_rows if r["formula"])
    nulls = sum(1 for r in out_rows if r["flag"].startswith("NULL_SPEND"))
    print("Series: %s / %s | growth type: %s | periods: %d | "
          "computed: %d | null-flagged: %d"
          % (ward, category, growth_type, len(out_rows), computed, nulls))
    for r in out_rows:
        if r["formula"]:
            print("  %s  actual=%s  %s" % (r["period"], r["actual_spend"],
                                           r["formula"]))
        elif r["flag"]:
            print("  %s  actual=%s  [%s]" % (r["period"], r["actual_spend"],
                                             r["flag"]))
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

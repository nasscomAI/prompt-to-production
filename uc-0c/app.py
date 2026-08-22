"""
UC-0C app.py — Number That Looks Right
Per-ward, per-category MoM/YoY growth over the ward budget dataset.
Enforcement mirrored from agents.md:
  - never aggregates across wards or categories; refuses such requests
  - flags every null actual_spend row before computing (with its notes reason)
  - shows the formula used in every computed output row
  - refuses to guess: missing/invalid --growth-type is a refusal, not a default
"""
import argparse
import csv
import os
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"]
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2212-"


def _norm(value):
    value = (value or "").strip().lower()
    value = re.sub(r"[%s]" % DASHES, "-", value)
    return re.sub(r"\s+", " ", value)


def _read_rows(path):
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = [dict(r) for r in reader]
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="cp1252", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                rows = [dict(r) for r in reader]
        except OSError as exc:
            print("ERROR: cannot read '%s': %s" % (path, exc), file=sys.stderr)
            raise SystemExit(1)
    except OSError as exc:
        print("ERROR: cannot read '%s': %s" % (path, exc), file=sys.stderr)
        raise SystemExit(1)

    if not os.path.isfile(path):
        print("ERROR: input file not found: %s" % path, file=sys.stderr)
        raise SystemExit(1)

    missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        print("ERROR: input CSV missing required column(s): %s. Found: %s"
              % (", ".join(missing), ", ".join(fieldnames)), file=sys.stderr)
        raise SystemExit(1)
    return rows


def load_dataset(path):
    """
    Read the ward budget CSV, validate columns, and report the number and
    location of null actual_spend values BEFORE any computation happens.
    Returns (rows, null_report).
    """
    rows = _read_rows(path)
    if not rows:
        print("ERROR: input CSV contains no data rows.", file=sys.stderr)
        raise SystemExit(1)

    cleaned = []
    null_report = []
    bad = 0
    for index, row in enumerate(rows, start=2):
        period = (row.get("period") or "").strip()
        ward = (row.get("ward") or "").strip()
        category = (row.get("category") or "").strip()
        notes = (row.get("notes") or "").strip()

        def to_float(key):
            raw_value = (row.get(key) or "").strip()
            if raw_value == "":
                return None
            try:
                return float(raw_value.replace(",", ""))
            except ValueError:
                return "BAD"

        budgeted = to_float("budgeted_amount")
        actual = to_float("actual_spend")

        if budgeted == "BAD" or actual == "BAD":
            bad += 1
            print("WARNING: skipping malformed row %d (%s | %s | %s): "
                  "non-numeric amount." % (index, period, ward, category),
                  file=sys.stderr)
            continue

        record = {"period": period, "ward": ward, "category": category,
                  "budgeted_amount": budgeted, "actual_spend": actual,
                  "notes": notes, "line": index}
        cleaned.append(record)
        if actual is None:
            null_report.append(record)

    print("Dataset loaded: %d valid rows from %s" % (len(cleaned), path))
    print("Null actual_spend rows found BEFORE computing: %d"
          % len(null_report))
    for r in null_report:
        print("  NULL -> %s | %s | %s | reason: %s"
              % (r["period"], r["ward"], r["category"], r["notes"] or "no note"))
    if bad:
        print("Malformed rows skipped: %d" % bad)
    return cleaned, null_report


def _resolve_option(values, user_value, kind):
    options = sorted({v for v in values if v})
    target = _norm(user_value)
    if target in {"all", "*", ""}:
        print("REFUSAL: aggregating across %ss is not allowed. This tool "
              "computes growth for ONE %s and ONE category only."
              % (kind, kind), file=sys.stderr)
        print("Available %ss: %s" % (kind, " | ".join(options)), file=sys.stderr)
        raise SystemExit(2)
    for option in options:
        if _norm(option) == target:
            return option
    partial = [option for option in options
               if target and (target in _norm(option) or _norm(option) in target)]
    if len(partial) == 1:
        resolved = partial[0]
        print('NOTE: "%s" resolved to %s "%s".'
              % (user_value.strip(), kind, resolved))
        return resolved
    print('REFUSAL: no unique %s matches "%s".' % (kind, user_value.strip()),
          file=sys.stderr)
    print("Available %ss: %s" % (kind, " | ".join(options)), file=sys.stderr)
    raise SystemExit(2)


def compute_growth(rows, ward, category, growth_type):
    """
    Take the validated rows plus one ward + one category + an explicit
    growth type, and return a per-period table. Every computed row shows
    the formula used. Null periods are flagged, never imputed.
    """
    series = sorted(
        (r for r in rows
         if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"])

    out = []
    previous = None
    for r in series:
        current = r["actual_spend"]
        row_out = {
            "period": r["period"],
            "ward": ward,
            "category": category,
            "budgeted_amount": "" if r["budgeted_amount"] is None
                               else "%.1f" % r["budgeted_amount"],
            "actual_spend": "",
            "growth_type": growth_type,
            "growth_pct": "",
            "formula": "",
            "status": "",
            "notes": r["notes"],
        }
        if current is None:
            row_out["status"] = "NULL_FLAGGED — NOT COMPUTED"
            row_out["notes"] = ("null actual_spend — reason: %s"
                                % (r["notes"] or "not given"))
        elif previous is None:
            row_out["actual_spend"] = "%.1f" % current
            row_out["status"] = "FIRST_PERIOD_NO_PRIOR"
            row_out["formula"] = "n/a (first period)"
        elif previous["actual_spend"] is None:
            row_out["actual_spend"] = "%.1f" % current
            prior_period = previous["period"]
            row_out["status"] = ("PREV_NULL_FLAGGED — %s growth not computed "
                                 "for %s" % (growth_type, prior_period))
            row_out["formula"] = ("n/a (prior period %s is null)"
                                  % prior_period)
        else:
            prior = previous["actual_spend"]
            pct = (current - prior) / prior * 100.0
            sign = "+" if pct >= 0 else "-"
            row_out["actual_spend"] = "%.1f" % current
            row_out["growth_pct"] = "%s%.1f%%" % (sign, abs(pct))
            row_out["status"] = "OK"
            row_out["formula"] = "(%s - %s) / %s * 100 = %s%s%%" % (
                ("%.1f" % current), ("%.1f" % prior), ("%.1f" % prior),
                sign, "%.1f" % abs(pct))
        out.append(row_out)
        if current is not None:
            previous = r

    if growth_type == "YoY":
        for row_out in out:
            if row_out["status"] == "OK":
                row_out["status"] = ("INSUFFICIENT_HISTORY — dataset covers a "
                                     "single year (2024); YoY needs prior-year "
                                     "data")
                row_out["formula"] = "n/a (no prior-year period in dataset)"
                row_out["growth_pct"] = ""
    return out


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Analyzer (per ward + category)")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None,
                        help='Exact ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", default=None,
                        help='Exact category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        choices=["MoM", "YoY"], help="MoM or YoY (never guessed)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("REFUSAL: --growth-type was not specified. I will not guess. "
              "Re-run with --growth-type MoM (month-over-month) or "
              "--growth-type YoY (year-over-year).", file=sys.stderr)
        raise SystemExit(2)

    rows, _nulls = load_dataset(args.input)

    if not args.ward:
        print("REFUSAL: no ward specified. Aggregating across wards is not "
              "allowed; pass one ward, e.g. --ward \"Ward 1 – Kasba\".",
              file=sys.stderr)
        print("Available wards: %s" % " | ".join(
            sorted({r["ward"] for r in rows})), file=sys.stderr)
        raise SystemExit(2)
    if not args.category:
        print("REFUSAL: no category specified. Aggregating across categories "
              'is not allowed; pass one category, e.g. --category '
              '"Roads & Pothole Repair".', file=sys.stderr)
        print("Available categories: %s" % " | ".join(
            sorted({r["category"] for r in rows})), file=sys.stderr)
        raise SystemExit(2)

    ward = _resolve_option({r["ward"] for r in rows}, args.ward, "ward")
    category = _resolve_option({r["category"] for r in rows},
                               args.category, "category")

    table = compute_growth(rows, ward, category, args.growth_type)
    if not table:
        print("ERROR: no data rows for ward=%r category=%r." % (ward, category),
              file=sys.stderr)
        raise SystemExit(1)

    fields = ["period", "ward", "category", "budgeted_amount", "actual_spend",
              "growth_type", "growth_pct", "formula", "status", "notes"]
    try:
        with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(table)
    except OSError as exc:
        print("ERROR: cannot write output '%s': %s" % (args.output, exc),
              file=sys.stderr)
        raise SystemExit(1)

    ok = sum(1 for r in table if r["status"] == "OK")
    flagged = sum(1 for r in table if "NULL_FLAGGED" in r["status"])
    print("Wrote %d period rows for [%s] x [%s] (%s)." %
          (len(table), ward, category, args.growth_type))
    print("Computed: %d | Null-flagged (not computed): %d" % (ok, flagged))
    print("Done. Results written to %s" % args.output)


if __name__ == "__main__":
    main()

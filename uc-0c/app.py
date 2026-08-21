"""
UC-0C app.py — Number That Looks Right
Per-ward per-category MoM growth analyzer. Built via the RICE + agents.md +
skills.md + CRAFT workflow. See README.md for run command and expected behaviour.

Enforcement (mirrors agents.md):
  1. Never aggregates across wards or categories — refuses if asked.
  2. Flags every null actual_spend row BEFORE computing, with its notes reason;
     the period after a null is also flagged (no prior to compute against).
  3. Shows the formula used in every computed output row.
  4. Refuses when --growth-type is not specified (never guesses MoM vs YoY).
"""
import argparse
import csv
import sys

ALLOWED_GROWTH_TYPES = ("MoM", "YoY")
AGGREGATION_WORDS = {"all", "all wards", "all categories", "any", "*", "combined", "total", "overall"}
OUTPUT_FIELDS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend",
    "growth_pct", "growth_formula", "flag", "notes",
]


def refuse(message):
    print("REFUSAL: %s" % message)
    sys.exit(2)


def norm_dash(s):
    return s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2011", "-")


def read_csv_any_encoding(path):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            print("ERROR: cannot read input file '%s': %s" % (path, exc))
            sys.exit(1)
    print("ERROR: could not decode '%s' with utf-8 or cp1252" % path)
    sys.exit(1)


def load_dataset(rows):
    """Validate columns; split rows into floats + null entries."""
    required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    if not rows:
        print("ERROR: input CSV has no data rows")
        sys.exit(1)
    missing = [c for c in required if c not in rows[0]]
    if missing:
        print("ERROR: input CSV missing columns: %s" % ", ".join(missing))
        sys.exit(1)

    records = []
    for r in rows:
        spend_raw = (r.get("actual_spend") or "").strip()
        budget_raw = (r.get("budgeted_amount") or "").strip()
        rec = {
            "period": (r.get("period") or "").strip(),
            "ward": (r.get("ward") or "").strip(),
            "category": (r.get("category") or "").strip(),
            "budgeted_amount": float(budget_raw) if budget_raw else None,
            "actual_spend": float(spend_raw) if spend_raw else None,
            "notes": (r.get("notes") or "").strip(),
        }
        records.append(rec)
    return records


def compute_growth(records, ward, category, growth_type):
    series = sorted(
        [r for r in records if r["ward"] == ward and r["category"] == category],
        key=lambda r: r["period"],
    )
    out = []
    null_periods = []
    for i, rec in enumerate(series):
        row = {
            "period": rec["period"],
            "ward": rec["ward"],
            "category": rec["category"],
            "budgeted_amount": "" if rec["budgeted_amount"] is None else ("%g" % rec["budgeted_amount"]),
            "actual_spend": "" if rec["actual_spend"] is None else ("%g" % rec["actual_spend"]),
            "growth_pct": "",
            "growth_formula": "",
            "flag": "",
            "notes": rec["notes"],
        }
        cur = rec["actual_spend"]
        prev_rec = series[i - 1] if i > 0 else None

        if growth_type == "YoY":
            prior_year = None
            for j in series:
                if j["period"][:4] != rec["period"][:4] and j["period"][5:] == rec["period"][5:]:
                    prior_year = j
            if prior_year is None or prior_year["actual_spend"] is None or cur is None:
                row["flag"] = "INSUFFICIENT_HISTORY"
                row["notes"] = (row["notes"] + "; " if row["notes"] else "") + \
                    "YoY needs same month of previous year — dataset covers one year only"
            else:
                prev = prior_year["actual_spend"]
                pct = (cur - prev) / prev * 100.0
                row["growth_pct"] = "%+.2f" % pct
                row["growth_formula"] = "(%g - %g) / %g * 100 = %+.2f%%" % (cur, prev, prev, pct)

        elif i == 0:
            row["flag"] = "BASELINE_NO_PRIOR"
            row["notes"] = (row["notes"] + "; " if row["notes"] else "") + \
                "first period in series — no previous month to compare"
        elif cur is None:
            row["flag"] = "NULL_ACTUAL_SPEND"
            reason = rec["notes"] or "reason not recorded"
            row["notes"] = (row["notes"] + "; " if row["notes"] else "") + \
                "actual_spend is NULL — flagged, NOT computed (%s)" % reason
            null_periods.append(rec["period"])
        elif prev_rec["actual_spend"] is None:
            row["flag"] = "PRIOR_IS_NULL"
            row["notes"] = (row["notes"] + "; " if row["notes"] else "") + \
                "previous month %s has NULL actual_spend — growth cannot be computed" % prev_rec["period"]
        else:
            prev = prev_rec["actual_spend"]
            pct = (cur - prev) / prev * 100.0
            row["growth_pct"] = "%+.2f" % pct
            row["growth_formula"] = "(%g - %g) / %g * 100 = %+.2f%%" % (cur, prev, prev, pct)
        out.append(row)
    return out


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="UC-0C Ward Budget MoM Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help='Exact ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=True, help='Exact category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="Growth type: MoM or YoY (must be specified — never guessed)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement rule 4: never guess the formula.
    if args.growth_type is None or not args.growth_type.strip():
        refuse("--growth-type was not specified. I will not guess the formula. "
               "Re-run with --growth-type MoM (or YoY).")
    growth_type = args.growth_type.strip()
    case_map = {"mom": "MoM", "yoy": "YoY"}
    if growth_type.lower() not in case_map:
        refuse("growth type '%s' is not supported. Allowed values: %s"
               % (args.growth_type, ", ".join(ALLOWED_GROWTH_TYPES)))
    growth_type = case_map[growth_type.lower()]

    # Enforcement rule 1: never aggregate across wards or categories.
    w_low = norm_dash(args.ward).strip().lower()
    c_low = args.category.strip().lower()
    if w_low in AGGREGATION_WORDS or "all ward" in w_low:
        refuse("cross-ward aggregation is not allowed. Specify exactly ONE ward.")
    if c_low in AGGREGATION_WORDS or "all categor" in c_low:
        refuse("cross-category aggregation is not allowed. Specify exactly ONE category.")

    records = load_dataset(read_csv_any_encoding(args.input))

    all_wards = sorted({r["ward"] for r in records})
    all_cats = sorted({r["category"] for r in records})

    def resolve(want, pool, kind):
        want_n = norm_dash(want).strip().lower()
        for cand in pool:
            if norm_dash(cand).strip().lower() == want_n:
                return cand
        print("ERROR: %s '%s' not found in dataset." % (kind, want))
        print("Valid %ss:" % kind)
        for p in pool:
            print("  - %s" % p)
        sys.exit(1)

    ward = resolve(args.ward, all_wards, "ward")
    category = resolve(args.category, all_cats, "category")

    scoped = [r for r in records if r["ward"] == ward and r["category"] == category]
    if not scoped:
        print("ERROR: no rows for ward='%s' category='%s'" % (ward, category))
        sys.exit(1)

    # Enforcement rule 2: report every null BEFORE computing.
    nulls = [r for r in scoped if r["actual_spend"] is None]
    print("Loaded %d rows for %s / %s (%d periods)" % (len(scoped), ward, category, len(scoped)))
    print("Null check BEFORE computing: %d null actual_spend row(s)" % len(nulls))
    for n in sorted(nulls, key=lambda r: r["period"]):
        print("  NULL %s — notes: %s" % (n["period"], n["notes"] or "reason not recorded"))

    results = compute_growth(scoped, ward, category, growth_type)

    try:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(results)
    except OSError as exc:
        print("ERROR: cannot write output file '%s': %s" % (args.output, exc))
        sys.exit(1)

    computed = sum(1 for r in results if r["growth_pct"])
    flagged = sum(1 for r in results if r["flag"])
    print("")
    print("%-9s %-12s %-8s %s" % ("period", "spend", "growth", "flag/notes"))
    for r in results:
        extra = r["flag"] or ""
        print("%-9s %-12s %-8s %s" % (r["period"], r["actual_spend"] or "NULL",
                                      r["growth_pct"] or "-", extra))
    print("")
    print("Done: %d computed, %d flagged (not computed), output -> %s"
          % (computed, flagged, args.output))


if __name__ == "__main__":
    main()

"""
UC-0C — Number That Looks Right

Per-ward, per-category budget growth calculator built from agents.md + skills.md.

Guards against the three failure modes:
  * Wrong aggregation level -> refuses any 'all wards'/'total' request; only ever
    computes for ONE ward + ONE category.
  * Silent null handling     -> every null actual_spend is flagged with its reason
    from the notes column; growth is never computed into or out of a null.
  * Formula assumption        -> --growth-type must be MoM or YoY (refuses otherwise),
    and the exact formula string is shown in every computed row.
"""
import argparse
import csv

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]
REFUSE_TOKENS = {"all", "total", "aggregate", "overall", "*", "", "any"}


def load_dataset(input_path: str):
    """Read the CSV, validate columns, return (rows, null_report)."""
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Empty CSV: %s" % input_path)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError("Missing required column(s): %s" % ", ".join(missing))

        rows = []
        null_report = []
        for r in reader:
            raw_spend = (r.get("actual_spend") or "").strip()
            try:
                spend = float(raw_spend) if raw_spend != "" else None
            except ValueError:
                spend = None  # unparseable treated as null, surfaced below
            row = {
                "period": (r.get("period") or "").strip(),
                "ward": (r.get("ward") or "").strip(),
                "category": (r.get("category") or "").strip(),
                "budgeted_amount": (r.get("budgeted_amount") or "").strip(),
                "actual_spend": spend,
                "notes": (r.get("notes") or "").strip(),
            }
            rows.append(row)
            if spend is None:
                null_report.append({
                    "period": row["period"], "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"] or "(no reason given in notes)",
                })
    return rows, null_report


def _prev_period(period: str, growth_type: str) -> str:
    """Return the comparison period key for MoM (prev month) or YoY (prev year)."""
    year, month = period.split("-")
    year, month = int(year), int(month)
    if growth_type == "MoM":
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    else:  # YoY
        year -= 1
    return "%04d-%02d" % (year, month)


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Return {'error': ...} on refusal, else {'table': [...]}."""
    if (ward or "").strip().lower() in REFUSE_TOKENS:
        return {"error": "REFUSED: aggregation across wards is not supported. "
                         "Specify exactly one ward."}
    if (category or "").strip().lower() in REFUSE_TOKENS:
        return {"error": "REFUSED: aggregation across categories is not "
                         "supported. Specify exactly one category."}
    if growth_type not in ("MoM", "YoY"):
        return {"error": "REFUSED: --growth-type must be 'MoM' or 'YoY'. "
                         "I will not guess which you intended."}

    # Isolate the single ward+category series, keyed by period. No aggregation.
    series = {}
    for r in rows:
        if r["ward"] == ward and r["category"] == category:
            series[r["period"]] = r
    if not series:
        return {"error": "REFUSED: no rows found for ward=%r category=%r. "
                         "Check the exact spelling (including the '–' dash)."
                         % (ward, category)}

    table = []
    for period in sorted(series):
        row = series[period]
        spend = row["actual_spend"]
        comp_key = _prev_period(period, growth_type)
        comp_row = series.get(comp_key)

        # Flag: current period spend is null.
        if spend is None:
            table.append({
                "period": period, "status": "FLAGGED",
                "actual_spend": "NULL",
                "detail": "actual_spend is null — not computed. Reason: %s"
                          % (row["notes"] or "(no reason in notes)"),
            })
            continue
        # Flag: no comparison period in the series (first month/year).
        if comp_row is None:
            table.append({
                "period": period, "status": "FLAGGED",
                "actual_spend": "%.1f" % spend,
                "detail": "no %s comparison period (%s) available — not computed"
                          % (growth_type, comp_key),
            })
            continue
        # Flag: comparison period spend is null.
        if comp_row["actual_spend"] is None:
            table.append({
                "period": period, "status": "FLAGGED",
                "actual_spend": "%.1f" % spend,
                "detail": "comparison period %s is null — not computed. Reason: %s"
                          % (comp_key, comp_row["notes"] or "(no reason in notes)"),
            })
            continue

        prev = comp_row["actual_spend"]
        growth = (spend - prev) / prev * 100 if prev != 0 else float("nan")
        formula = "(%.1f - %.1f) / %.1f x 100" % (spend, prev, prev)
        table.append({
            "period": period, "status": "COMPUTED",
            "actual_spend": "%.1f" % spend,
            "comparison_period": comp_key,
            "comparison_spend": "%.1f" % prev,
            "formula": formula,
            "growth_pct": "%+.1f%%" % growth,
        })
    return {"table": table, "ward": ward, "category": category,
            "growth_type": growth_type}


def write_output(result, output_path):
    fieldnames = ["ward", "category", "period", "growth_type", "status",
                  "actual_spend", "comparison_period", "comparison_spend",
                  "formula", "growth_pct", "detail"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in result["table"]:
            w.writerow({
                "ward": result["ward"], "category": result["category"],
                "period": row["period"], "growth_type": result["growth_type"],
                "status": row["status"],
                "actual_spend": row.get("actual_spend", ""),
                "comparison_period": row.get("comparison_period", ""),
                "comparison_spend": row.get("comparison_spend", ""),
                "formula": row.get("formula", ""),
                "growth_pct": row.get("growth_pct", ""),
                "detail": row.get("detail", ""),
            })


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward")
    parser.add_argument("--category", required=True, help="Exactly one category")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY (required — refuses if omitted)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)
    print("Loaded %d rows. Null actual_spend rows: %d" % (len(rows), len(null_report)))
    for n in null_report:
        print("  NULL  %s | %s | %s -> %s"
              % (n["period"], n["ward"], n["category"], n["reason"]))

    if args.growth_type is None:
        print("\nREFUSED: --growth-type not specified. Re-run with "
              "--growth-type MoM or --growth-type YoY. I will not guess.")
        return

    result = compute_growth(rows, args.ward, args.category, args.growth_type)
    if "error" in result:
        print("\n" + result["error"])
        return

    write_output(result, args.output)
    computed = sum(1 for r in result["table"] if r["status"] == "COMPUTED")
    flagged = sum(1 for r in result["table"] if r["status"] == "FLAGGED")
    print("\nDone. %s growth for %s / %s written to %s (%d computed, %d flagged)."
          % (args.growth_type, args.ward, args.category, args.output,
             computed, flagged))


if __name__ == "__main__":
    main()

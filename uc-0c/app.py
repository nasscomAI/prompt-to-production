"""UC-0C growth calculator

CLI:
  python app.py --input ../data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys
from datetime import datetime


def parse_float(v):
    if v is None or v.strip() == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--ward", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--growth-type", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    if args.growth_type != "MoM":
        raise SystemExit("Unsupported growth-type. Only 'MoM' is supported.")

    rows = []
    with open(args.input, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)

    null_rows = [row for row in rows if parse_float(row.get("actual_spend", "")) is None]
    print(f"Detected {len(null_rows)} NULL actual_spend row(s) in the input dataset.", file=sys.stderr)
    for row in null_rows:
        print(
            f"NULL: {row.get('period')} | {row.get('ward')} | {row.get('category')} | {row.get('notes', '')}",
            file=sys.stderr,
        )

    # filter to ward and category
    scoped = [r for r in rows if r.get("ward") == args.ward and r.get("category") == args.category]
    if not scoped:
        raise SystemExit(f"No data found for ward='{args.ward}' and category='{args.category}'")

    # sort by period
    def period_key(r):
        return datetime.strptime(r["period"], "%Y-%m")
    scoped.sort(key=period_key)

    out_rows = []
    prev_actual = None
    for r in scoped:
        period = r["period"]
        actual = parse_float(r.get("actual_spend", ""))
        note = r.get("notes", "") or ""
        if actual is None or prev_actual is None:
            growth = "NOT_COMPUTED"
            formula = "((current_actual - previous_actual) / previous_actual) * 100"
            reason = "previous or current actual_spend is NULL; not computed"
            if actual is None and prev_actual is None:
                reason = "current and previous actual_spend NULL; not computed"
            elif actual is None:
                reason = "current actual_spend NULL; not computed"
            else:
                reason = "previous actual_spend NULL; not computed"
            out_rows.append({
                "period": period,
                "ward": args.ward,
                "category": args.category,
                "actual_spend": r.get("actual_spend", ""),
                "previous_actual": "" if prev_actual is None else str(prev_actual),
                "formula": formula,
                "growth": growth,
                "note": note or reason,
            })
        else:
            formula = "((current_actual - previous_actual) / previous_actual) * 100"
            growth_val = ((actual - prev_actual) / prev_actual) * 100
            growth = f"{growth_val:+.1f}%"
            out_rows.append({
                "period": period,
                "ward": args.ward,
                "category": args.category,
                "actual_spend": str(actual),
                "previous_actual": str(prev_actual),
                "formula": formula,
                "growth": growth,
                "note": note,
            })
        prev_actual = actual

    # write output
    fieldnames = ["period","ward","category","actual_spend","previous_actual","formula","growth","note"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)


if __name__ == "__main__":
    main()

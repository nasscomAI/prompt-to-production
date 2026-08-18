"""
UC-0C app.py — Budget growth (MoM) analysis for a single ward and category.
Outputs a per-period growth table to growth_output.csv.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH_TYPES = ("MoM", "YoY")
FORMULAS = {
    "MoM": "MoM = (current - previous) / previous x 100",
    "YoY": "YoY = (current - same period last year) / same period last year x 100",
}


def load_dataset(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            sys.exit("error: input CSV is empty")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            sys.exit(f"error: missing required column(s): {', '.join(missing)}")
        rows = list(reader)

    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    print(f"loaded {len(rows)} rows; {len(null_rows)} null actual_spend row(s)", file=sys.stderr)
    for r in null_rows:
        print(f"  null: {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes']}", file=sys.stderr)
    return rows


def compute_growth(rows, ward, category, growth_type):
    subset = sorted(
        [r for r in rows if r["ward"] == ward and r["category"] == category],
        key=lambda r: r["period"],
    )
    if not subset:
        sys.exit(f"refused: no data found for ward '{ward}' and category '{category}'")

    results = []
    previous = None
    formula = FORMULAS[growth_type]
    for row in subset:
        actual = row["actual_spend"].strip()
        period = row["period"]
        notes = row["notes"].strip()

        if not actual:
            results.append({
                "period": period,
                "actual_spend": "",
                "growth": "",
                "flag": "NULL_ACTUAL",
                "reason": notes or "actual_spend is null",
                "formula": formula,
            })
        elif previous is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": "",
                "flag": "NO_PREV",
                "reason": "no previous period for first record",
                "formula": formula,
            })
        else:
            current = float(actual)
            growth = (current - previous) / previous * 100
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": f"{growth:+0.1f}%",
                "flag": "OK",
                "reason": "",
                "formula": formula,
            })
        if actual:
            previous = float(actual)
    return results


def main():
    parser = argparse.ArgumentParser(description="Compute per-ward per-category growth.")
    parser.add_argument("--input", required=True, help="path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="single ward, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", required=True, help="single category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", choices=SUPPORTED_GROWTH_TYPES, help="growth metric to compute")
    parser.add_argument("--output", default="growth_output.csv", help="output CSV path")
    args = parser.parse_args()

    if not args.growth_type:
        sys.exit("refused: --growth-type is required (MoM or YoY); never guessing the formula")
    if args.ward.strip().lower() in ("all", "all wards") or args.category.strip().lower() in ("all", "all categories"):
        sys.exit("refused: scope wider than a single ward and single category is not allowed")

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "flag", "reason", "formula"])
        writer.writeheader()
        writer.writerows(results)

    print(f"wrote {len(results)} rows to {args.output}")
    for r in results:
        print(f"  {r['period']}: spend={r['actual_spend'] or 'NULL'} growth={r['growth'] or 'NULL'} flag={r['flag']}")


if __name__ == "__main__":
    main()

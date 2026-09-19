"""
UC-0C — Number That Looks Right

Per-ward, per-category growth calculator. Never adds wards or categories together:
every output row belongs to exactly one (ward, category, period). Null actual_spend
values are reported with the reason from the notes column and are never used as a value
in a computation. The growth formula is only applied when an explicit --growth-type
(MoM or YoY) is given; otherwise the run is refused.

Refusals come before any computation:
  * missing or unsupported --growth-type
  * missing --ward/--category, or unequal repeat counts (pairs are positional)
  * aggregate words (all, any, *, total, overall, combined, every)
  * unknown ward or category names (message names the valid alternatives)

Run command (from README):
  python app.py --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 - Kasba" --category "Roads & Pothole Repair" \
      --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = {"MoM", "YoY"}
AGGREGATE_WORDS = {"all", "any", "*", "total", "overall", "combined", "every"}
FORMULA = "(actual[{p}] - actual[{prev}]) / actual[{prev}] x 100"
OUTPUT_FIELDS = [
    "ward", "category", "period", "actual_spend", "compared_with", "previous_actual_spend",
    "growth_type", "growth_pct", "formula", "status", "note",
]


def refuse(msg):
    print(f"REFUSED: {msg}", file=sys.stderr)
    sys.exit(2)


def load_dataset(path):
    """Read the budget CSV, validate columns and report every null actual_spend row."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                refuse(f"{path} is missing required columns: {missing}")
            rows = list(reader)
    except FileNotFoundError:
        refuse(f"input file not found: {path}")

    nulls = []
    for r in rows:
        raw = (r["actual_spend"] or "").strip()
        r["actual"] = float(raw) if raw else None
        if r["actual"] is None:
            nulls.append(r)

    print(f"Loaded {len(rows)} rows from {path}.")
    print(f"Null actual_spend rows: {len(nulls)}")
    for r in nulls:
        print(f"  - {r['period']} | {r['ward']} | {r['category']} -> {r['notes'] or 'no reason given'}")
    return rows


def _previous_period(period, growth_type):
    year, month = int(period[:4]), int(period[5:7])
    if growth_type == "YoY":
        return f"{year - 1:04d}-{month:02d}"
    year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    return f"{year:04d}-{month:02d}"


def compute_growth(rows, ward, category, growth_type):
    """Return the per-period growth table for exactly one ward and one category."""
    subset = {r["period"]: r for r in rows if r["ward"] == ward and r["category"] == category}
    if not subset:
        refuse(f"no rows for ward '{ward}' + category '{category}'")

    table = []
    for period in sorted(subset):
        row = subset[period]
        prev_period = _previous_period(period, growth_type)
        prev = subset.get(prev_period)
        formula = FORMULA.format(p=period, prev=prev_period)
        out = {
            "ward": ward, "category": category, "period": period,
            "actual_spend": "" if row["actual"] is None else f"{row['actual']:.1f}",
            "compared_with": prev_period,
            "previous_actual_spend": "" if not prev or prev["actual"] is None else f"{prev['actual']:.1f}",
            "growth_type": growth_type, "growth_pct": "", "formula": formula,
            "status": "", "note": "",
        }
        if row["actual"] is None:
            out["status"] = "NULL_FLAGGED"
            out["note"] = f"actual_spend is null - {row['notes'] or 'no reason given'}; growth not computed"
        elif prev is None:
            out["status"] = "NO_PRIOR_PERIOD"
            out["note"] = f"no data for {prev_period} in the dataset; growth not computed"
        elif prev["actual"] is None:
            out["status"] = "PRIOR_NULL_FLAGGED"
            out["note"] = f"{prev_period} actual_spend is null - {prev['notes'] or 'no reason given'}; growth not computed"
        elif prev["actual"] == 0:
            out["status"] = "DIVIDE_BY_ZERO"
            out["note"] = f"{prev_period} actual_spend is 0; growth undefined"
        else:
            pct = (row["actual"] - prev["actual"]) / prev["actual"] * 100
            out["growth_pct"] = f"{pct:+.1f}%"
            out["formula"] = f"({row['actual']:.1f} - {prev['actual']:.1f}) / {prev['actual']:.1f} x 100"
            out["status"] = "OK"
        table.append(out)
    return table


def main():
    parser = argparse.ArgumentParser(description="UC-0C per-ward per-category growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", action="append", help="Exact ward name (repeatable)")
    parser.add_argument("--category", action="append", help="Exact category name (repeatable)")
    parser.add_argument("--growth-type", help="MoM or YoY - required, never assumed")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    # --- refusals come before any computation --------------------------------
    if not args.growth_type:
        refuse("--growth-type not given. Choose MoM (month-on-month) or YoY (year-on-year); "
               "the formula is not guessed.")
    if args.growth_type not in GROWTH_TYPES:
        refuse(f"--growth-type '{args.growth_type}' is not supported. Use MoM or YoY.")
    if not args.ward or not args.category:
        refuse("--ward and --category are both required - growth is computed per ward per "
               "category only; an all-ward or all-category figure is not produced.")
    if len(args.ward) != len(args.category):
        refuse("give the same number of --ward and --category values; they are paired in order.")
    for value in args.ward + args.category:
        if value.strip().lower() in AGGREGATE_WORDS:
            refuse(f"'{value}' asks for an aggregate across wards/categories. Name one ward "
                   "and one category per pair.")

    rows = load_dataset(args.input)
    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    for w, c in zip(args.ward, args.category):
        if w not in wards:
            refuse(f"unknown ward '{w}'. Valid wards: {wards}")
        if c not in categories:
            refuse(f"unknown category '{c}'. Valid categories: {categories}")

    table = []
    for w, c in zip(args.ward, args.category):
        table.extend(compute_growth(rows, w, c, args.growth_type))

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(table)

    flagged = [t for t in table if t["status"] != "OK"]
    print(f"Wrote {len(table)} rows ({len(table) - len(flagged)} computed, {len(flagged)} flagged) "
          f"to {args.output}")


if __name__ == "__main__":
    main()
"""
UC-0C app.py — Ward budget growth calculator.
Built from uc-0c/agents.md (RICE enforcement) and uc-0c/skills.md.

One ward + one category + an explicit growth type in, one row per period
out, with the formula shown on every row. Null actual_spend rows are
reported up front and never computed across. All-ward / all-category
aggregation and a missing growth type are refused, not guessed.
"""
import argparse
import csv
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = {"MOM": "MoM", "YOY": "YoY"}
AGGREGATE_REQUESTS = {"", "all", "*", "any", "all wards", "all categories", "total"}
OUTPUT_FIELDS = ["period", "ward", "category", "actual_spend", "previous_period",
                 "previous_spend", "growth_pct", "formula", "flag"]


def refuse(message: str):
    print(f"REFUSED: {message}", file=sys.stderr)
    sys.exit(2)


def _norm(name: str) -> str:
    # Treat "Ward 1 - Kasba" and "Ward 1 – Kasba" as the same name.
    return re.sub(r"\s*[-–—]\s*", " – ", name.strip()).lower()


def load_dataset(path: str):
    """Read the CSV, validate it, and report every null actual_spend row before returning."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                sys.exit(f"Error: input CSV is missing column(s): {', '.join(missing)}")
            raw_rows = list(reader)
    except FileNotFoundError:
        sys.exit(f"Error: input file not found: {path}")

    rows, null_rows = [], []
    for line_no, raw in enumerate(raw_rows, start=2):
        period = raw["period"].strip()
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period):
            sys.exit(f"Error: line {line_no}: malformed period '{period}' (expected YYYY-MM)")
        try:
            budgeted = float(raw["budgeted_amount"])
            actual_text = raw["actual_spend"].strip()
            actual = float(actual_text) if actual_text else None
        except ValueError:
            sys.exit(f"Error: line {line_no}: non-numeric budgeted_amount or actual_spend — not coerced to 0")
        row = {
            "period": period,
            "ward": raw["ward"].strip(),
            "category": raw["category"].strip(),
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "notes": (raw["notes"] or "").strip(),
        }
        rows.append(row)
        if actual is None:
            null_rows.append(row)

    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(null_rows)}")
    for r in null_rows:
        print(f"  NULL  {r['period']} · {r['ward']} · {r['category']} — reason: {r['notes'] or 'not given'}")
    return rows, null_rows


def _fmt(value):
    return "" if value is None else f"{value:g}"


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Return one row per period for a single ward + category, with the formula shown."""
    if growth_type is None or not growth_type.strip():
        refuse("--growth-type was not specified. Growth can be month-over-month (MoM) or "
               "year-over-year (YoY) and they give different answers. Re-run with "
               "--growth-type MoM or --growth-type YoY; this tool will not pick one for you.")
    gtype = GROWTH_TYPES.get(growth_type.strip().upper())
    if gtype is None:
        refuse(f"Unsupported --growth-type '{growth_type}'. Use MoM or YoY.")

    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    for label, value, valid in (("ward", ward, wards), ("category", category, categories)):
        if value is None or value.strip().lower() in AGGREGATE_REQUESTS or "," in value:
            refuse(f"Aggregating across {label}s is not allowed — a combined figure hides "
                   f"per-{label} differences and null rows. Ask for one {label} at a time. "
                   f"Valid {label}s: {'; '.join(valid)}")
    ward_match = next((w for w in wards if _norm(w) == _norm(ward)), None)
    category_match = next((c for c in categories if c.lower() == category.strip().lower()), None)
    if ward_match is None:
        refuse(f"Ward '{ward}' not found. Valid wards: {'; '.join(wards)}")
    if category_match is None:
        refuse(f"Category '{category}' not found. Valid categories: {'; '.join(categories)}")

    series = {r["period"]: r for r in rows if r["ward"] == ward_match and r["category"] == category_match}
    table = []
    for period in sorted(series):
        current = series[period]
        year, month = int(period[:4]), int(period[5:])
        if gtype == "MoM":
            prev_period = f"{year - 1}-12" if month == 1 else f"{year}-{month - 1:02d}"
        else:
            prev_period = f"{year - 1}-{month:02d}"
        previous = series.get(prev_period)
        cur_val = current["actual_spend"]
        prev_val = previous["actual_spend"] if previous else None

        growth, flag = "", ""
        if cur_val is None:
            flag = f"NULL_CURRENT: {current['notes'] or 'actual_spend missing'} — growth not computed"
            formula = f"{gtype} = (NULL - {_fmt(prev_val) or 'n/a'}) / {_fmt(prev_val) or 'n/a'} × 100"
        elif previous is None:
            flag = f"NO_PRIOR_PERIOD: {prev_period} not in dataset — growth not computed"
            formula = f"{gtype} = (current - previous) / previous × 100; previous ({prev_period}) unavailable"
        elif prev_val is None:
            flag = f"NULL_PREVIOUS: {prev_period} is null ({previous['notes'] or 'actual_spend missing'}) — growth not computed"
            formula = f"{gtype} = ({_fmt(cur_val)} - NULL) / NULL × 100"
        elif prev_val == 0:
            flag = "ZERO_PREVIOUS: previous spend is 0 — growth undefined"
            formula = f"{gtype} = ({_fmt(cur_val)} - 0) / 0 × 100"
        else:
            pct = (cur_val - prev_val) / prev_val * 100
            growth = f"{pct:+.1f}"
            formula = f"{gtype} = ({_fmt(cur_val)} - {_fmt(prev_val)}) / {_fmt(prev_val)} × 100 = {growth}%"

        table.append({
            "period": period,
            "ward": ward_match,
            "category": category_match,
            "actual_spend": _fmt(cur_val) or "NULL",
            "previous_period": prev_period,
            "previous_spend": _fmt(prev_val) if previous else "",
            "growth_pct": growth,
            "formula": formula,
            "flag": flag,
        })
    return table


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help='Exact ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", help='Exact category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY (required — never assumed)")
    parser.add_argument("--output", required=True, help="Path to write the growth CSV")
    args = parser.parse_args()

    rows, _ = load_dataset(args.input)
    table = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(table)

    flagged = [r for r in table if r["flag"]]
    print(f"{len(table)} periods written for {table[0]['ward']} · {table[0]['category']} "
          f"({len(flagged)} flagged, growth not computed).")
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

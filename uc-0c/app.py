"""
UC-0C — Number That Looks Right
Deterministic ward-level budget growth calculator. Implements the contracts
defined in agents.md and skills.md: strict single-ward single-category scope,
explicit flagging of every null actual_spend with its notes reason, formula
shown on every computed row, and refusal to guess an unspecified growth type.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ("period", "ward", "category", "budgeted_amount", "actual_spend", "notes")
OUTPUT_COLUMNS = (
    "period", "ward", "category", "budgeted_amount", "actual_spend",
    "growth_type", "growth_pct", "formula", "flag", "notes",
)
GROWTH_TYPES = {"mom": "MoM", "yoy": "YoY"}
AGGREGATION_REQUESTS = {"all", "*", "total", "totals", "aggregate", "combined", "overall"}

FLAG_NO_PRIOR = "NO_PRIOR_PERIOD"
FLAG_NULL_CURRENT = "NULL_SPEND"
FLAG_NULL_PRIOR = "PRIOR_SPEND_NULL"
FLAG_ZERO_PRIOR = "PRIOR_SPEND_ZERO"
FLAG_UNPARSEABLE = "UNPARSEABLE_SPEND"


def load_dataset(path):
    """Read the budget CSV; validate columns; report nulls before returning."""
    try:
        input_file = open(path, newline="", encoding="utf-8")
    except OSError as exc:
        sys.exit(f"error: cannot read input file '{path}': {exc}")

    with input_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            sys.exit(f"error: input CSV is missing required columns: {', '.join(missing)}")
        rows = []
        for line_no, row in enumerate(reader, start=2):
            row["_line"] = line_no
            rows.append(row)

    if not rows:
        sys.exit("error: input CSV contains no data rows")

    known_wards = sorted({r["ward"].strip() for r in rows})
    known_categories = sorted({r["category"].strip() for r in rows})
    null_report = [
        {
            "line": r["_line"],
            "period": r["period"].strip(),
            "ward": r["ward"].strip(),
            "category": r["category"].strip(),
            "notes": r["notes"].strip(),
        }
        for r in rows if not r["actual_spend"].strip()
    ]
    return rows, known_wards, known_categories, null_report


def _prior_period(period, growth_type):
    year, month = int(period[:4]), int(period[5:7])
    if growth_type == "MoM":
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    else:
        year -= 1
    return f"{year:04d}-{month:02d}"


def _row(ward, category, period, budget, spend_raw, growth_type):
    return {
        "period": period,
        "ward": ward,
        "category": category,
        "budgeted_amount": budget,
        "actual_spend": spend_raw if spend_raw else "NULL",
        "growth_type": growth_type,
        "growth_pct": "",
        "formula": "",
        "flag": "",
        "notes": "",
    }


def compute_growth(rows, ward, category, growth_type):
    """Return one output row per period for the requested ward+category slice."""
    series = {}
    for r in rows:
        if r["ward"].strip() == ward and r["category"].strip() == category:
            series[r["period"].strip()] = r

    table = []
    for period in sorted(series):
        r = series[period]
        budget = r["budgeted_amount"].strip()
        spend_raw = r["actual_spend"].strip()
        note = r["notes"].strip()
        out = _row(ward, category, period, budget, spend_raw, growth_type)
        out["notes"] = note

        if not spend_raw:
            out["flag"] = FLAG_NULL_CURRENT
            out["notes"] = note or "reason not recorded"
            table.append(out)
            continue

        try:
            cur = float(spend_raw)
        except ValueError:
            out["flag"] = FLAG_UNPARSEABLE
            out["notes"] = (note + "; " if note else "") + f"actual_spend {spend_raw!r} is not a number"
            table.append(out)
            continue

        prior_period = _prior_period(period, growth_type)
        prior = series.get(prior_period)
        if prior is None:
            out["flag"] = FLAG_NO_PRIOR
            out["notes"] = note or f"no {prior_period} row exists for this ward+category"
            table.append(out)
            continue

        prior_raw = prior["actual_spend"].strip()
        if not prior_raw:
            prior_note = prior["notes"].strip() or "reason not recorded"
            out["flag"] = FLAG_NULL_PRIOR
            out["notes"] = f"{prior_period} actual_spend is NULL ({prior_note}) — not computed"
            table.append(out)
            continue

        try:
            prev = float(prior_raw)
        except ValueError:
            out["flag"] = FLAG_UNPARSEABLE
            out["notes"] = f"{prior_period} actual_spend {prior_raw!r} is not a number"
            table.append(out)
            continue

        if prev == 0:
            out["flag"] = FLAG_ZERO_PRIOR
            out["notes"] = f"growth undefined: {prior_period} actual_spend is 0"
            table.append(out)
            continue

        pct = round((cur - prev) / prev * 100, 1)
        out["growth_pct"] = f"{pct:+.1f}%"
        out["formula"] = f"({cur:g} − {prev:g}) / {prev:g} × 100 = {pct:+.1f}%"
        table.append(out)

    return table


def _refuse_aggregation(value, kind):
    sys.exit(
        f"refused: '{value}' is not a single {kind}. This tool computes growth for "
        f"exactly one {kind} at a time and never aggregates across wards or "
        "categories. Pass one of the exact values listed by this tool."
    )


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name from the dataset")
    parser.add_argument("--category", required=True, help="Exact category name from the dataset")
    parser.add_argument("--growth-type", default=None, help="MoM or YoY — no default is assumed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type or not args.growth_type.strip():
        sys.exit(
            "refused: no growth type specified. Choose explicitly: "
            "--growth-type MoM (vs previous month) or --growth-type YoY "
            "(vs same month previous year). Never guessed."
        )
    growth_key = args.growth_type.strip().lower()
    if growth_key not in GROWTH_TYPES:
        sys.exit(
            f"refused: unknown growth type '{args.growth_type}'. "
            f"Supported types: MoM, YoY."
        )
    growth_type = GROWTH_TYPES[growth_key]

    rows, known_wards, known_categories, null_report = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows | {len(known_wards)} wards x "
          f"{len(known_categories)} categories | periods "
          f"{min(r['period'] for r in rows)} .. {max(r['period'] for r in rows)}")

    print(f"Null audit BEFORE computing: {len(null_report)} blank actual_spend row(s)")
    for n in null_report:
        print(f"  - line {n['line']}: {n['period']} | {n['ward']} | "
              f"{n['category']} | reason: {n['notes'] or 'not recorded'}")

    if args.ward.strip().lower() in AGGREGATION_REQUESTS:
        _refuse_aggregation(args.ward.strip(), "ward")
    if args.category.strip().lower() in AGGREGATION_REQUESTS:
        _refuse_aggregation(args.category.strip(), "category")

    if args.ward.strip() not in known_wards:
        sys.exit(
            f"refused: ward {args.ward!r} not found. Valid wards:\n  "
            + "\n  ".join(known_wards)
        )
    if args.category.strip() not in known_categories:
        sys.exit(
            f"refused: category {args.category!r} not found. Valid categories:\n  "
            + "\n  ".join(known_categories)
        )

    table = compute_growth(rows, args.ward.strip(), args.category.strip(), growth_type)

    computed = sum(1 for t in table if t["formula"])
    flagged = len(table) - computed
    with open(args.output, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(table)

    print(f"Wrote {args.output}: {len(table)} rows | {computed} computed | "
          f"{flagged} flagged (never silently skipped)")


if __name__ == "__main__":
    main()

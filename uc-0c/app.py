"""
UC-0C app.py — Budget Growth Calculator
Built with the RICE → agents.md → skills.md → CRAFT workflow.
Enforcement rules mirror uc-0c/agents.md: no cross-ward/category aggregation,
null rows flagged (never computed), formula shown per row, growth-type required.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ("MoM", "YoY")
AGGREGATE_TOKENS = {"", "all", "any", "*", "all wards", "all categories"}


def refuse(message: str):
    """Emit a refusal and exit non-zero (agents.md refusal condition)."""
    print(f"REFUSED: {message}", file=sys.stderr)
    sys.exit(2)


def parse_spend(raw: str):
    """Blank/null actual_spend -> None (never 0)."""
    if raw is None:
        return None
    value = raw.strip()
    if value == "" or value.lower() == "null":
        return None
    return float(value)


def load_dataset(input_path: str):
    """Read CSV, validate columns, report null rows before returning."""
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing_cols = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            rows = list(reader)
    except FileNotFoundError:
        refuse(f"Input file not found: {input_path}")

    if not rows:
        refuse(f"Input file is empty: {input_path}")

    parsed = []
    for r in rows:
        parsed.append({
            "period": r["period"].strip(),
            "ward": r["ward"].strip(),
            "category": r["category"].strip(),
            "budgeted_amount": r["budgeted_amount"].strip(),
            "actual_spend": parse_spend(r["actual_spend"]),
            "notes": (r["notes"] or "").strip(),
        })

    nulls = [r for r in parsed if r["actual_spend"] is None]
    print(f"Loaded {len(parsed)} rows. Null actual_spend rows: {len(nulls)}")
    for r in nulls:
        print(f"  NULL · {r['period']} · {r['ward']} · {r['category']} "
              f"— reason: {r['notes'] or 'no note provided'}")
    return parsed


def prev_period(period: str, growth_type: str):
    """Return the comparison period key for MoM (prev month) or YoY (prev year)."""
    year, month = (int(x) for x in period.split("-"))
    if growth_type == "MoM":
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    else:  # YoY
        year -= 1
    return f"{year:04d}-{month:02d}"


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Per-period MoM/YoY growth for one ward+category, with formula shown."""
    if growth_type not in VALID_GROWTH_TYPES:
        refuse(f"--growth-type must be one of {VALID_GROWTH_TYPES}; got '{growth_type}'. "
               f"Refusing to guess a formula.")
    if ward.strip().lower() in AGGREGATE_TOKENS:
        refuse("Cross-ward aggregation is not allowed. Specify a single ward.")
    if category.strip().lower() in AGGREGATE_TOKENS:
        refuse("Cross-category aggregation is not allowed. Specify a single category.")

    known_wards = {r["ward"] for r in rows}
    known_categories = {r["category"] for r in rows}
    if ward not in known_wards:
        refuse(f"Unknown ward '{ward}'. Known wards: {sorted(known_wards)}")
    if category not in known_categories:
        refuse(f"Unknown category '{category}'. Known categories: {sorted(known_categories)}")

    series = {r["period"]: r for r in rows
              if r["ward"] == ward and r["category"] == category}
    periods = sorted(series)

    out = []
    for period in periods:
        row = series[period]
        current = row["actual_spend"]
        comp_key = prev_period(period, growth_type)
        comp_row = series.get(comp_key)
        comp_value = comp_row["actual_spend"] if comp_row else None

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "NULL" if current is None else current,
            "comparison_period": comp_key,
            "comparison_value": "NULL" if comp_value is None else (comp_value if comp_row else "N/A"),
            "growth_type": growth_type,
            "formula": "",
            "growth_pct": "NULL",
            "flag": "",
        }

        if current is None:
            result["flag"] = f"CURRENT_NULL — {row['notes'] or 'no note'}"
        elif comp_row is None:
            result["flag"] = f"NO_COMPARISON_PERIOD ({comp_key} not in dataset)"
        elif comp_value is None:
            result["flag"] = f"COMPARISON_NULL — {comp_row['notes'] or 'no note'}"
        else:
            growth = (current - comp_value) / comp_value * 100
            result["formula"] = f"{growth_type} = ({current} - {comp_value}) / {comp_value} * 100"
            result["growth_pct"] = f"{growth:+.1f}%"

        out.append(result)
    return out


OUTPUT_FIELDS = ["period", "ward", "category", "actual_spend", "comparison_period",
                 "comparison_value", "growth_type", "formula", "growth_pct", "flag"]


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward name")
    parser.add_argument("--category", required=True, help="Single category name")
    # No default — a missing/invalid value must be refused, not guessed.
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY (required — no default)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    if args.growth_type is None:
        refuse("--growth-type is required (MoM or YoY). Refusing to guess a formula.")

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    computed = sum(1 for r in results if r["growth_pct"] != "NULL")
    flagged = sum(1 for r in results if r["flag"])
    print(f"Done. {len(results)} periods for {args.ward} / {args.category}: "
          f"{computed} computed, {flagged} flagged. Written to {args.output}")


if __name__ == "__main__":
    main()

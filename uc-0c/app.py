"""
UC-0C app.py — Ward Budget Growth Calculator
Built from agents.md (RICE) and skills.md via the CRAFT workflow.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

MONTHS_OFFSET = {"MoM": 1, "YoY": 12}


def load_dataset(file_path: str):
    """
    Read ward_budget.csv, validate columns, and report null actual_spend
    rows before returning the data. Nulls are never dropped or coerced.
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required column(s) in {file_path}: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if not r["actual_spend"].strip()]

    print(f"Loaded {len(rows)} rows. {len(null_rows)} row(s) have null actual_spend:")
    for r in null_rows:
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes'] or '(no reason given)'}")

    return rows, null_rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str):
    """
    Compute per-period growth for a single ward + category. Refuses to
    aggregate across wards/categories and refuses on missing/invalid
    growth_type. Null actual_spend periods are flagged, never computed.
    """
    if not growth_type or growth_type not in MONTHS_OFFSET:
        raise ValueError(
            "growth_type must be explicitly 'MoM' or 'YoY' — refusing to guess a default."
        )

    matching = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not matching:
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'. "
            "Refusing to aggregate across wards/categories to produce a result."
        )

    matching.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in matching}
    offset = MONTHS_OFFSET[growth_type]
    formula_desc = "(current_actual_spend - previous_actual_spend) / previous_actual_spend * 100"

    output_rows = []
    for row in matching:
        period = row["period"]
        year, month = int(period[:4]), int(period[5:7])
        prev_month_total = (year * 12 + (month - 1)) - offset
        prev_year, prev_month = divmod(prev_month_total, 12)
        prev_month += 1
        prev_period = f"{prev_year:04d}-{prev_month:02d}"

        prev_row = by_period.get(prev_period)
        current_spend = row["actual_spend"].strip()
        prev_spend = prev_row["actual_spend"].strip() if prev_row else ""

        if not prev_row:
            output_rows.append({
                "period": period, "actual_spend": current_spend or "",
                "growth_pct": "", "formula": formula_desc,
                "flag": f"NO_PRIOR_PERIOD ({prev_period} not in dataset)",
            })
        elif not current_spend or not prev_spend:
            reason = row["notes"] if not current_spend else prev_row["notes"]
            output_rows.append({
                "period": period, "actual_spend": current_spend or "NULL",
                "growth_pct": "", "formula": formula_desc,
                "flag": f"NULL_SPEND: {reason or 'no reason given'}",
            })
        else:
            growth = (float(current_spend) - float(prev_spend)) / float(prev_spend) * 100
            output_rows.append({
                "period": period, "actual_spend": current_spend,
                "growth_pct": f"{growth:.1f}%", "formula": formula_desc,
                "flag": "",
            })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", dest="growth_type", default=None, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    if not args.growth_type:
        sys.exit("Refusing to run: --growth-type not specified. Must be MoM or YoY.")

    rows, _ = load_dataset(args.input)

    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        sys.exit(f"Refused: {e}")

    fieldnames = ["period", "actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Budget Growth Calculator
Built using RICE -> agents.md -> skills.md workflow.
"""
import argparse
import csv
import sys


def load_dataset(input_path: str):
    """
    Reads the ward budget CSV, validates columns, and reports null
    actual_spend rows before any computation happens.
    Returns: (rows, null_rows)
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])
            missing = required_columns - fieldnames
            if missing:
                raise ValueError(f"Input CSV is missing required columns: {sorted(missing)}")
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    null_rows = []
    for row in rows:
        if row.get("actual_spend", "").strip() == "":
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "").strip() or "No reason given in notes column",
            })

    return rows, null_rows


def compute_growth(ward: str, category: str, growth_type: str, rows: list):
    """
    Computes MoM or YoY growth for one ward and one category across all
    available periods, showing the formula used. Refuses to aggregate
    across multiple wards/categories.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'. "
            "I will not guess a growth type — please specify one explicitly."
        )

    # filter to exactly this ward + category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'. "
            "Refusing to aggregate across wards/categories to find a substitute."
        )

    # build a period -> row lookup, restricted to this ward+category only
    by_period = {}
    for r in filtered:
        spend_str = r.get("actual_spend", "").strip()
        by_period[r["period"]] = {
            "actual_spend": float(spend_str) if spend_str != "" else None,
            "notes": r.get("notes", "").strip(),
        }

    sorted_periods = sorted(by_period.keys())

    output_rows = []
    for period in sorted_periods:
        current = by_period[period]

        # determine comparison period
        if growth_type == "MoM":
            year, month = period.split("-")
            year, month = int(year), int(month)
            if month == 1:
                comp_year, comp_month = year - 1, 12
            else:
                comp_year, comp_month = year, month - 1
            comp_period = f"{comp_year:04d}-{comp_month:02d}"
            formula = "(current - previous_month) / previous_month * 100"
        else:  # YoY
            year, month = period.split("-")
            comp_period = f"{int(year) - 1:04d}-{month}"
            formula = "(current - same_month_last_year) / same_month_last_year * 100"

        comp = by_period.get(comp_period)

        row_out = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current["actual_spend"],
            "growth_percent": "",
            "formula_used": formula,
            "flag": "",
        }

        if current["actual_spend"] is None:
            row_out["flag"] = f"NULL_ACTUAL_SPEND: {current['notes'] or 'No reason given'}"
        elif comp is None:
            row_out["flag"] = f"NO_COMPARISON_PERIOD ({comp_period} not in dataset)"
        elif comp["actual_spend"] is None:
            row_out["flag"] = f"COMPARISON_PERIOD_NULL ({comp_period}): {comp['notes'] or 'No reason given'}"
        else:
            prev = comp["actual_spend"]
            curr = current["actual_spend"]
            if prev == 0:
                row_out["flag"] = "PREVIOUS_PERIOD_ZERO: cannot compute percentage growth"
            else:
                growth = (curr - prev) / prev * 100
                row_out["growth_percent"] = round(growth, 1)

        output_rows.append(row_out)

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=False, default=None,
                         help="MoM or YoY (required — no default guessing)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print(
            "ERROR: --growth-type was not specified. This tool refuses to guess "
            "between MoM and YoY. Please re-run with --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} total rows. Found {len(null_rows)} rows with null actual_spend:")
    for nr in null_rows:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['reason']}")

    try:
        results = compute_growth(args.ward, args.category, args.growth_type, rows)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_percent", "formula_used", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
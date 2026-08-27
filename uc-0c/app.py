"""
UC-0C — Municipal Budget Growth Analysis
Computes period-over-period growth for a single ward + category combination.
No cross-ward or cross-category aggregation is performed.
"""
import argparse
import csv
import sys

OUTPUT_FIELDS = ["period", "ward", "category", "actual_spend",
                 "growth_type", "growth_percent", "formula", "flag"]

MOM_FORMULA = "(current_spend - previous_spend) / previous_spend * 100"


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(path: str) -> list[dict]:
    """
    Load ward_budget.csv, validate required columns, detect null actual_spend rows.
    Returns list of row dicts (actual_spend is float or None).
    Prints a null-row report before returning.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not required_cols.issubset(set(reader.fieldnames or [])):
                missing = required_cols - set(reader.fieldnames or [])
                sys.exit(f"Error: missing required columns: {', '.join(missing)}")
            rows = list(reader)
    except OSError as exc:
        sys.exit(f"Error: cannot read dataset '{path}': {exc}")

    # Normalise actual_spend to float | None; collect nulls for reporting
    null_rows: list[dict] = []
    parsed: list[dict] = []
    for row in rows:
        raw = row["actual_spend"].strip()
        if raw == "":
            row["_spend"] = None
            null_rows.append(row)
        else:
            try:
                row["_spend"] = float(raw)
            except ValueError:
                row["_spend"] = None
                null_rows.append(row)
        parsed.append(row)

    # Report nulls upfront (agents.md: report before computing)
    if null_rows:
        print(f"\nNULL actual_spend detected in {len(null_rows)} row(s):")
        for r in null_rows:
            reason = r["notes"].strip() or "No reason provided"
            print(f"  [{r['period']}] {r['ward']} / {r['category']} — {reason}")
        print()

    return parsed


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list[dict], ward: str, category: str,
                   growth_type: str) -> list[dict]:
    """
    Filter to the requested ward+category and compute MoM growth per period.
    Returns list of output row dicts ready for CSV writing.
    """
    # Strict single-ward / single-category enforcement (agents.md)
    filtered = [r for r in rows
                if r["ward"] == ward and r["category"] == category]

    if not filtered:
        sys.exit(
            f"Error: no data found for ward='{ward}', category='{category}'. "
            "Check the exact values in the CSV."
        )

    # Sort chronologically by period (YYYY-MM strings sort correctly)
    filtered.sort(key=lambda r: r["period"])

    output: list[dict] = []
    prev_spend: float | None = None
    prev_period: str | None = None

    for row in filtered:
        period = row["period"]
        spend = row["_spend"]
        notes = row["notes"].strip()

        if spend is None:
            # Null row — flag it, do not compute
            reason = notes or "actual_spend is null"
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": "",
                "flag": f"NULL_SPEND: {reason}",
            })
            # Do not update prev_spend so the next period is also flagged
            # if it depends on this missing value
            prev_spend = None
            prev_period = period
            continue

        if prev_spend is None:
            # First valid period or period after a null — no previous to compare
            flag = "NO_PREVIOUS" if prev_period is not None else "FIRST_PERIOD"
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": MOM_FORMULA,
                "flag": flag,
            })
        else:
            growth = (spend - prev_spend) / prev_spend * 100
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth_type": growth_type,
                "growth_percent": round(growth, 2),
                "formula": MOM_FORMULA,
                "flag": "",
            })

        prev_spend = spend
        prev_period = period

    return output


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True, help="Exact ward name to analyse")
    parser.add_argument("--category",    required=True, help="Exact category to analyse")
    parser.add_argument("--growth-type", required=True,
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM (Month over Month) or YoY (Year over Year)")
    parser.add_argument("--output",      required=True, help="Path for results CSV")
    args = parser.parse_args()

    if args.growth_type == "YoY":
        sys.exit("Error: YoY growth requires at least 13 months of data. "
                 "Only MoM is supported for this dataset (12 periods). "
                 "Please pass --growth-type MoM.")

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(results)
    except OSError as exc:
        sys.exit(f"Error: cannot write output file '{args.output}': {exc}")

    # Console summary
    computed = sum(1 for r in results if r["growth_percent"] != "")
    flagged  = sum(1 for r in results if r["flag"])
    print(f"Done. {len(results)} rows written to {args.output}")
    print(f"  Computed: {computed}  |  Flagged / skipped: {flagged}")


if __name__ == "__main__":
    main()

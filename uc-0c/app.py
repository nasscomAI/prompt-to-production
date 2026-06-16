"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth skills per agents.md RICE rules.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ── Skill: load_dataset ────────────────────────────────────────────────────────
def load_dataset(input_path: str, ward: str, category: str) -> tuple[list[dict], list[dict]]:
    """
    Read ward_budget.csv, validate columns, filter to ward+category,
    report nulls before returning. Never silently imputes nulls.
    Returns (rows, null_report).
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])
            missing_cols = REQUIRED_COLUMNS - fieldnames
            if missing_cols:
                sys.exit(
                    f"ERROR: Missing required columns: {sorted(missing_cols)}\n"
                    f"       Found: {sorted(fieldnames)}"
                )
            all_rows = list(reader)
    except FileNotFoundError:
        sys.exit(f"ERROR: Input file not found: '{input_path}'")

    # Filter to requested ward + category
    filtered = [r for r in all_rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        wards      = sorted({r["ward"]     for r in all_rows})
        categories = sorted({r["category"] for r in all_rows})
        sys.exit(
            f"ERROR: No rows found for ward='{ward}' category='{category}'.\n"
            f"  Valid wards      : {wards}\n"
            f"  Valid categories : {categories}"
        )

    # Parse actual_spend; identify nulls
    rows: list[dict] = []
    null_report: list[dict] = []

    for r in filtered:
        raw_spend = r["actual_spend"].strip()
        spend = None if raw_spend == "" else float(raw_spend)
        row = {
            "period":          r["period"].strip(),
            "ward":            r["ward"].strip(),
            "category":        r["category"].strip(),
            "budgeted_amount": float(r["budgeted_amount"]),
            "actual_spend":    spend,
            "notes":           r["notes"].strip(),
        }
        rows.append(row)
        if spend is None:
            null_report.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "reason":   row["notes"] or "No reason provided in notes column",
            })

    # Print null report before any computation (enforcement rule 2)
    if null_report:
        print(f"\nNULL ACTUAL_SPEND — {len(null_report)} row(s) flagged before computation:")
        for n in null_report:
            print(f"  {n['period']}  {n['ward']} / {n['category']}")
            print(f"    Reason: {n['reason']}")
        print()

    rows.sort(key=lambda r: r["period"])
    return rows, null_report


# ── Skill: compute_growth ──────────────────────────────────────────────────────
def compute_growth(rows: list[dict], growth_type: str, null_periods: set) -> list[dict]:
    """
    Compute per-period growth rates for a single ward+category.
    Shows formula in every output row. Skips and flags null periods.
    Refuses if growth_type is not exactly 'MoM' or 'YoY'.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be exactly 'MoM' or 'YoY' — got '{growth_type}'. "
            "Please specify explicitly; never guessed."
        )

    # Enforcement: refuse if rows span >1 ward or category
    wards      = {r["ward"]     for r in rows}
    categories = {r["category"] for r in rows}
    if len(wards) > 1 or len(categories) > 1:
        raise ValueError(
            f"compute_growth received data spanning multiple wards/categories — "
            f"wards: {wards}, categories: {categories}. "
            "Cross-ward and cross-category aggregation is not permitted."
        )

    if growth_type == "YoY":
        ordered = sorted(rows, key=lambda r: r["period"])
        period_to_row = {r["period"]: r for r in ordered}
    else:
        ordered = rows  # already sorted by period

    # Insufficient data guard (skills.md: fewer than 2 non-null rows → refuse)
    non_null_count = sum(1 for r in ordered if r["actual_spend"] is not None and r["period"] not in null_periods)
    if non_null_count < 2:
        print("Insufficient non-null data to compute growth.")
        return []

    results: list[dict] = []

    for i, row in enumerate(ordered):
        period  = row["period"]
        spend   = row["actual_spend"]

        # Flag and skip null rows (enforcement rule 2)
        if period in null_periods or spend is None:
            results.append({
                "period":       period,
                "ward":         row["ward"],
                "category":     row["category"],
                "actual_spend": None,
                "growth_pct":   None,
                "formula":      "NULL — not computed. See null report above.",
                "flag":         "NULL_SKIPPED",
            })
            continue

        # Determine prior period value
        prior_spend = None

        if growth_type == "MoM" and i > 0:
            prior_row = ordered[i - 1]
            if prior_row["actual_spend"] is not None and prior_row["period"] not in null_periods:
                prior_spend = prior_row["actual_spend"]

        elif growth_type == "YoY":
            year  = int(period[:4])
            month = period[5:]
            prior_key = f"{year - 1}-{month}"
            prior_row = period_to_row.get(prior_key)
            if prior_row and prior_row["actual_spend"] is not None and prior_key not in null_periods:
                prior_spend = prior_row["actual_spend"]

        # Base period or prior is null → not computable
        if prior_spend is None:
            results.append({
                "period":       period,
                "ward":         row["ward"],
                "category":     row["category"],
                "actual_spend": spend,
                "growth_pct":   None,
                "formula":      f"No prior {growth_type} period available — base period.",
                "flag":         "",
            })
            continue

        # Compute growth and show formula (enforcement rule 3)
        growth_pct = ((spend - prior_spend) / prior_spend) * 100
        sign       = "+" if growth_pct >= 0 else ""
        formula    = (
            f"{growth_type}: ({spend} - {prior_spend}) / {prior_spend} x 100 "
            f"= {sign}{growth_pct:.1f}%"
        )

        results.append({
            "period":       period,
            "ward":         row["ward"],
            "category":     row["category"],
            "actual_spend": spend,
            "growth_pct":   round(growth_pct, 1),
            "formula":      formula,
            "flag":         "",
        })

    return results


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement rule 4: refuse if --growth-type not specified
    if not args.growth_type:
        sys.exit(
            "ERROR: --growth-type not specified.\n"
            "Please provide exactly 'MoM' (month-on-month) or 'YoY' (year-on-year).\n"
            "This value is never guessed — it must be explicit."
        )

    # Skill 1: load
    rows, null_report = load_dataset(args.input, args.ward, args.category)
    null_periods = {n["period"] for n in null_report}

    print(f"Loaded {len(rows)} rows for: {args.ward} / {args.category}")

    # Skill 2: compute
    try:
        results = compute_growth(rows, args.growth_type, null_periods)
    except ValueError as e:
        sys.exit(f"ERROR: {e}")

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print results table to stdout
    print(f"\n{'Period':<10} {'Actual Spend':>14} {'Growth':>9}  Formula")
    print("-" * 75)
    for r in results:
        spend  = f"Rs.{r['actual_spend']:.1f}L" if r["actual_spend"] is not None else "NULL"
        growth = f"{r['growth_pct']:+.1f}%" if r["growth_pct"] is not None else "—"
        print(f"{r['period']:<10} {spend:>14} {growth:>9}  {r['formula']}")

    print(f"\nDone. Results written to {args.output}")
    print(f"  Rows computed  : {sum(1 for r in results if r['growth_pct'] is not None)}")
    print(f"  Nulls skipped  : {sum(1 for r in results if r['flag'] == 'NULL_SKIPPED')}")


if __name__ == "__main__":
    main()

"""
UC-0C — Budget Growth Analysis Agent
Generated from agents.md and skills.md.

Agent contract (agents.md):
  role      : Compute MoM or YoY growth for a single ward + category only.
              Never aggregate across wards/categories. Never guess growth type.
  intent    : Per-period table — formula shown with values, nulls flagged before
              computation, every row verifiable against source CSV.
  enforcement:
    1. Refuse all-ward / all-category aggregation requests.
    2. Flag every null actual_spend row (with notes reason) before computing.
    3. Show formula with substituted values in every output row.
    4. Refuse if --growth-type not specified — never default silently.

Skills (skills.md):
  load_dataset(file_path)                            → {data, null_rows, null_count}
  compute_growth(data, ward, category, growth_type)  → per-period list with formula
"""
import argparse
import csv
import os

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: load_dataset  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────
def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate required columns, and return data plus a
    mandatory null report.

    Returns dict with:
      - data       : list of row dicts (all rows, unmodified)
      - null_rows  : list of dicts for rows where actual_spend is null/blank
      - null_count : int

    Error handling (skills.md):
      - FileNotFoundError  if file cannot be read
      - ValueError         if any required column is missing
      - Null report is always included — never suppressed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        raw_rows = list(reader)
        actual_columns = set(reader.fieldnames or [])

    missing_cols = REQUIRED_COLUMNS - actual_columns
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_cols))}")

    data = []
    null_rows = []

    for row in raw_rows:
        spend_raw = row.get("actual_spend", "").strip()
        row["_actual_spend_null"] = (spend_raw == "")
        row["_actual_spend_float"] = None if row["_actual_spend_null"] else float(spend_raw)
        data.append(row)

        if row["_actual_spend_null"]:
            null_rows.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "notes":    row.get("notes", "").strip() or "(no reason given)",
            })

    return {"data": data, "null_rows": null_rows, "null_count": len(null_rows)}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: compute_growth  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────
def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter to the given ward + category, then compute per-period growth.

    Returns list of dicts (chronological), each with:
      period, actual_spend, growth (% 2dp or None), formula (str), status (str)

    Error handling (skills.md):
      - ValueError for unknown growth_type (never default silently).
      - ValueError if ward+category combination yields zero rows.
      - Null rows → growth=None, formula="N/A", never skipped.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "Growth type not specified. "
            "Please provide --growth-type MoM or --growth-type YoY."
        )

    filtered = [
        r for r in data
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward='{ward}' category='{category}'. "
            "Check that the ward and category names match the CSV exactly."
        )

    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        spend  = row["_actual_spend_float"]

        if spend is None:
            results.append({
                "period": period, "actual_spend": None,
                "growth": None, "formula": "N/A",
                "status": "NOT COMPUTED - null actual_spend",
            })
            continue

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period, "actual_spend": spend,
                    "growth": None, "formula": "N/A",
                    "status": "NOT COMPUTED - no prior period",
                })
                continue
            prev_row   = filtered[i - 1]
            prev_spend = prev_row["_actual_spend_float"]
            prev_label = prev_row["period"]
        else:  # YoY
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
            prior_matches = [r for r in filtered if r["period"] == prior_period]
            if not prior_matches:
                results.append({
                    "period": period, "actual_spend": spend,
                    "growth": None, "formula": "N/A",
                    "status": f"NOT COMPUTED - no prior year period ({prior_period})",
                })
                continue
            prev_row   = prior_matches[0]
            prev_spend = prev_row["_actual_spend_float"]
            prev_label = prior_period

        if prev_spend is None:
            results.append({
                "period": period, "actual_spend": spend,
                "growth": None, "formula": "N/A",
                "status": f"NOT COMPUTED - prior period ({prev_label}) has null actual_spend",
            })
            continue

        growth  = ((spend - prev_spend) / prev_spend) * 100
        formula = f"(({spend} - {prev_spend}) / {prev_spend}) * 100"

        results.append({
            "period": period, "actual_spend": spend,
            "growth": round(growth, 2), "formula": formula,
            "status": "OK",
        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────────────────────────────────────
def _print_null_report(null_rows: list):
    print(f"\n{'='*60}")
    print(f"NULL REPORT — {len(null_rows)} null actual_spend row(s) found")
    print(f"{'='*60}")
    for nr in null_rows:
        print(f"  {nr['period']}  |  {nr['ward']}  |  {nr['category']}")
        print(f"           Reason: {nr['notes']}")
    print()


def _print_growth_table(results: list, ward: str, category: str, growth_type: str):
    print(f"{'='*60}")
    print(f"GROWTH TABLE  [{growth_type}]")
    print(f"Ward    : {ward}")
    print(f"Category: {category}")
    print(f"{'='*60}")
    print(f"{'Period':<12} {'Actual Spend':>14} {'Growth %':>10}  Status")
    print(f"{'-'*60}")
    for row in results:
        spend_str  = f"{row['actual_spend']:.1f}" if row["actual_spend"] is not None else "NULL"
        growth_str = f"{row['growth']:+.2f}%" if row["growth"] is not None else "—"
        print(f"{row['period']:<12} {spend_str:>14} {growth_str:>10}  {row['status']}")
        if row["status"] == "OK":
            print(f"{'':>12}   formula: {row['formula']}")
    print()


def _write_output_csv(results: list, ward: str, category: str,
                      growth_type: str, output_path: str):
    fieldnames = ["period", "ward", "category", "growth_type",
                  "actual_spend", "growth_pct", "formula", "status"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({
                "period":       row["period"],
                "ward":         ward,
                "category":     category,
                "growth_type":  growth_type,
                "actual_spend": row["actual_spend"] if row["actual_spend"] is not None else "",
                "growth_pct":   row["growth"] if row["growth"] is not None else "",
                "formula":      row["formula"],
                "status":       row["status"],
            })


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis Agent")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, default=None,
                        dest="growth_type",
                        help="MoM or YoY (required — will refuse if omitted)")
    parser.add_argument("--output",      required=True,  help="Path to write results CSV")
    args = parser.parse_args()

    # Enforcement rule 4: refuse if growth_type not specified
    if args.growth_type is None:
        print("ERROR: Growth type not specified. "
              "Please provide --growth-type MoM or --growth-type YoY.")
        raise SystemExit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Unknown growth type '{args.growth_type}'. "
              "Please provide --growth-type MoM or --growth-type YoY.")
        raise SystemExit(1)

    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset['data'])} rows from {args.input}")

    # Enforcement rule 2: print null report before computation
    _print_null_report(dataset["null_rows"])

    results = compute_growth(
        data=dataset["data"], ward=args.ward,
        category=args.category, growth_type=args.growth_type,
    )

    _print_growth_table(results, args.ward, args.category, args.growth_type)
    _write_output_csv(results, args.ward, args.category, args.growth_type, args.output)
    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()

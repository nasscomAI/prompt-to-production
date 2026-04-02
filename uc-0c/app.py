"""
UC-0C — Number That Looks Right

Computes per-period MoM or YoY spend growth for a specified ward and category.

Enforcement:
  - Never aggregates across wards or categories — refuses if not specified
  - Flags all null actual_spend rows before computing
  - Shows formula in every output row
  - Refuses if --growth-type not specified

Run:
  python app.py \\
    --input ../data/budget/ward_budget.csv \\
    --ward "Ward 1 – Kasba" \\
    --category "Roads & Pothole Repair" \\
    --growth-type MoM \\
    --output growth_output.csv
"""

import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str, ward: str, category: str) -> dict:
    """
    Load ward_budget.csv, validate, filter to ward+category, report nulls.
    """
    # Refusal: refuse aggregation if ward or category is blank/all
    if not ward or ward.strip().lower() in ("", "all"):
        sys.exit(
            "ERROR: Aggregation across wards not permitted. "
            "Specify an exact --ward value."
        )
    if not category or category.strip().lower() in ("", "all"):
        sys.exit(
            "ERROR: Aggregation across categories not permitted. "
            "Specify an exact --category value."
        )

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)
            actual_cols = set(reader.fieldnames or [])
    except FileNotFoundError:
        sys.exit(f"ERROR: File not found: {file_path}")

    missing_cols = REQUIRED_COLUMNS - actual_cols
    if missing_cols:
        sys.exit(f"ERROR: Missing required columns: {', '.join(missing_cols)}")

    # Filter to exact ward + category
    filtered = [
        r for r in raw_rows
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        available_wards = sorted({r["ward"] for r in raw_rows})
        available_cats = sorted({r["category"] for r in raw_rows})
        sys.exit(
            f"ERROR: No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Identify null rows
    null_rows = [
        r for r in filtered
        if r["actual_spend"].strip() == ""
    ]

    return {
        "rows": filtered,
        "null_rows": null_rows,
        "total_rows": len(filtered),
    }


def compute_growth(rows: list, null_rows: list, growth_type: str) -> list:
    """
    Compute per-period growth with formula shown. Never guesses growth type.
    """
    if growth_type not in ("MoM", "YoY"):
        sys.exit(
            "ERROR: Please specify --growth-type MoM or YoY. "
            "This system will not guess."
        )

    null_periods = {r["period"] for r in null_rows}
    period_to_spend = {}
    for r in rows:
        spend = r["actual_spend"].strip()
        period_to_spend[r["period"]] = float(spend) if spend else None

    periods = sorted(period_to_spend.keys())
    results = []

    for i, period in enumerate(periods):
        current = period_to_spend[period]
        null_reason = ""
        # Find the null reason from notes if applicable
        for r in rows:
            if r["period"] == period and r["actual_spend"].strip() == "":
                null_reason = r.get("notes", "").strip()

        if period in null_periods:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "formula": "NULL — not computed",
                "growth": f"NOT_COMPUTED ({period} actual_spend is null)",
                "null_reason": null_reason,
            })
            continue

        # Find prior period
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "actual_spend": str(current),
                    "formula": "N/A (first period)",
                    "growth": "N/A",
                    "null_reason": "",
                })
                continue
            prior_period = periods[i - 1]
        else:  # YoY
            # Find period 12 months prior
            year, month = period.split("-")
            prior_period = f"{int(year)-1}-{month}"
            if prior_period not in period_to_spend:
                results.append({
                    "period": period,
                    "actual_spend": str(current),
                    "formula": "N/A (no prior year data)",
                    "growth": "N/A",
                    "null_reason": "",
                })
                continue

        prior = period_to_spend[prior_period]

        if prior is None:
            results.append({
                "period": period,
                "actual_spend": str(current),
                "formula": f"NOT_COMPUTED — prior period {prior_period} is null",
                "growth": f"NOT_COMPUTED (prior period {prior_period} is null)",
                "null_reason": "",
            })
            continue

        if prior == 0:
            results.append({
                "period": period,
                "actual_spend": str(current),
                "formula": f"({current} - {prior}) / {prior} * 100 — UNDEFINED (prior=0)",
                "growth": "NOT_COMPUTED (prior period spend is zero)",
                "null_reason": "",
            })
            continue

        raw_growth = (current - prior) / prior * 100
        sign = "+" if raw_growth >= 0 else ""
        formula_str = f"({current} - {prior}) / {prior} * 100"
        results.append({
            "period": period,
            "actual_spend": str(current),
            "formula": formula_str,
            "growth": f"{sign}{raw_growth:.1f}%",
            "null_reason": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        sys.exit(
            "ERROR: Please specify --growth-type MoM or YoY. "
            "This system will not guess."
        )

    dataset = load_dataset(args.input, args.ward, args.category)

    # Report nulls BEFORE computing
    if dataset["null_rows"]:
        print(f"\nNULL ROWS DETECTED ({len(dataset['null_rows'])} row(s)) — reported before computing:")
        for r in dataset["null_rows"]:
            print(f"  Period: {r['period']} | Ward: {r['ward']} | "
                  f"Category: {r['category']} | Reason: {r.get('notes', '').strip() or 'No notes'}")
        print()

    results = compute_growth(dataset["rows"], dataset["null_rows"], args.growth_type)

    fieldnames = ["period", "actual_spend", "formula", "growth", "null_reason"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth table ({args.growth_type}) written to {args.output}")
    print(f"Ward: {args.ward} | Category: {args.category}")
    print(f"Periods: {len(results)} | Nulls flagged: {len(dataset['null_rows'])}")


if __name__ == "__main__":
    main()

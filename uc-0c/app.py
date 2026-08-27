"""
UC-0C — Number That Looks Right
Budget Growth Computation Agent for CMC Ward Budget data.
Computes MoM or YoY growth per ward per category — never aggregates across wards.

Run:
    python app.py \
      --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 – Kasba" \
      --category "Roads & Pothole Repair" \
      --growth-type MoM \
      --output growth_output.csv
"""
import argparse
import csv
import sys
from pathlib import Path


# ─── Skill: load_dataset ───────────────────────────────────────────────────────

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> dict:
    """
    Reads the ward_budget CSV file, validates columns, reports null rows.
    Returns: dict with data, null_rows, row_count, null_count
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"Dataset file is empty: {file_path}")

    # Validate columns
    actual_cols = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - actual_cols
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = []
    null_rows = []

    for row in rows:
        spend_raw = row.get("actual_spend", "").strip()
        is_null = spend_raw == "" or spend_raw is None

        parsed_row = {
            "period": row["period"].strip(),
            "ward": row["ward"].strip(),
            "category": row["category"].strip(),
            "budgeted_amount": float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else None,
            "actual_spend": float(spend_raw) if not is_null else None,
            "notes": row.get("notes", "").strip(),
            "is_null": is_null,
        }
        data.append(parsed_row)

        if is_null:
            null_rows.append({
                "period": parsed_row["period"],
                "ward": parsed_row["ward"],
                "category": parsed_row["category"],
                "null_reason": parsed_row["notes"] or "No reason provided in notes column",
            })

    # ENFORCEMENT: Report nulls BEFORE returning — never silently skip
    print(f"\nDataset loaded: {len(data)} rows.")
    print(f"NULL actual_spend rows detected: {len(null_rows)}")
    if null_rows:
        print("  The following rows have NULL actual_spend and will NOT be used in growth calculations:")
        for nr in null_rows:
            print(f"    [{nr['period']}] {nr['ward']} | {nr['category']} — Reason: {nr['null_reason']}")
    print("")

    return {
        "data": data,
        "null_rows": null_rows,
        "row_count": len(data),
        "null_count": len(null_rows),
    }


# ─── Skill: compute_growth ─────────────────────────────────────────────────────

def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Computes growth per period for the specified ward and category.
    Returns: list of dicts with period, actual_spend, growth_value, formula, null_reason

    ENFORCEMENT:
    - Never aggregate across wards or categories
    - Flag every null row — do not compute growth through nulls
    - Show exact formula for every row
    - Refuse if growth_type is not MoM or YoY
    """
    # Validate growth_type — REFUSE, never guess
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "Error: --growth-type is required. Specify MoM or YoY. Do not guess."
        )

    all_data = dataset["data"]

    # Validate ward exists
    available_wards = sorted(set(r["ward"] for r in all_data))
    if ward not in available_wards:
        raise ValueError(
            f"Ward not found: '{ward}'\nAvailable wards:\n" +
            "\n".join(f"  - {w}" for w in available_wards)
        )

    # Validate category exists
    available_cats = sorted(set(r["category"] for r in all_data))
    if category not in available_cats:
        raise ValueError(
            f"Category not found: '{category}'\nAvailable categories:\n" +
            "\n".join(f"  - {c}" for c in available_cats)
        )

    # ENFORCEMENT: Single ward, single category — no aggregation
    filtered = [
        r for r in all_data
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Build period → row lookup
    period_map = {r["period"]: r for r in filtered}
    results = []

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]
        null_reason = row["notes"] if row["is_null"] else ""
        growth_value = None
        formula = ""

        if row["is_null"]:
            formula = "NULL — actual_spend not available"
            growth_value = None
        else:
            # Find prior period
            if growth_type == "MoM":
                year, month = period.split("-")
                prev_month = int(month) - 1
                prev_year = int(year)
                if prev_month == 0:
                    prev_month = 12
                    prev_year -= 1
                prior_period = f"{prev_year}-{prev_month:02d}"
            else:  # YoY
                year, month = period.split("-")
                prior_period = f"{int(year)-1}-{month}"

            prior_row = period_map.get(prior_period)

            if prior_row is None:
                formula = f"No prior period ({prior_period}) in dataset — first row"
                growth_value = None
            elif prior_row["is_null"]:
                formula = (
                    f"Prior period {prior_period} actual_spend is NULL "
                    f"— cannot compute {growth_type} growth"
                )
                growth_value = None
            else:
                prior = prior_row["actual_spend"]
                if prior == 0:
                    formula = f"({actual} - {prior}) / {prior} × 100 = undefined (division by zero)"
                    growth_value = None
                else:
                    pct = ((actual - prior) / prior) * 100
                    growth_value = round(pct, 1)
                    sign = "+" if pct >= 0 else ""
                    formula = f"({actual} - {prior}) / {prior} × 100 = {sign}{growth_value}%"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual is not None else "NULL",
            "growth_value": f"{'+' if growth_value and growth_value >= 0 else ''}{growth_value}%" if growth_value is not None else "NULL",
            "formula": formula,
            "null_reason": null_reason,
        })

    return results


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Computation Agent (per-ward, per-category only)"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help='Ward name e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=True, help='Category e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM (Month-over-Month) or YoY (Year-over-Year) — REQUIRED, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # ENFORCEMENT: Refuse if growth-type not specified
    if not args.growth_type:
        print("Error: --growth-type is required. Specify MoM or YoY. Do not guess.", file=sys.stderr)
        sys.exit(1)

    # Load dataset (reports nulls automatically)
    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Compute growth
    try:
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_value", "formula", "null_reason"]
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Growth computation complete.")
    print(f"Ward: {args.ward}")
    print(f"Category: {args.category}")
    print(f"Growth type: {args.growth_type}")
    print(f"Periods computed: {len(results)}")
    null_periods = [r for r in results if r["actual_spend"] == "NULL"]
    if null_periods:
        print(f"NULL periods (not computed): {len(null_periods)}")
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()

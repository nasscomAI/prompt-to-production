"""
UC-0C app.py — Budget Growth Analyst
Computes MoM or YoY growth for a single ward + category pair.
Enforces: null flagging, formula display, no aggregation, explicit growth-type.

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


# ---------------------------------------------------------------------------
# SKILL: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str, ward: str, category: str):
    """
    Reads ward_budget.csv, validates columns, filters to one ward+category,
    and reports every null actual_spend row BEFORE returning data.

    Returns:
        filtered_rows  : list[dict]  — rows matching ward+category, sorted by period
        null_rows      : list[dict]  — {period, notes} for each null actual_spend row
    Raises:
        ValueError if required columns are missing or no rows match the filter.
    """
    required_columns = {"period", "ward", "category",
                        "budgeted_amount", "actual_spend", "notes"}

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            raise ValueError(f"CSV is missing required columns: {missing}")

        all_rows = list(reader)

    # Filter strictly to the requested ward + category — no mixing
    filtered_rows = [
        r for r in all_rows
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]

    if not filtered_rows:
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'. "
            "Check spelling and exact ward/category names."
        )

    # Sort by period (YYYY-MM strings sort lexicographically correctly)
    filtered_rows.sort(key=lambda r: r["period"])

    # Identify null rows and report them BEFORE any computation
    null_rows = []
    for r in filtered_rows:
        if r["actual_spend"].strip() == "":
            null_rows.append({"period": r["period"], "notes": r["notes"].strip()})

    if null_rows:
        print("\n⚠️  NULL actual_spend rows detected (flagged BEFORE growth computation):")
        for n in null_rows:
            reason = n["notes"] if n["notes"] else "No reason given"
            print(f"   • {n['period']}  →  {reason}")
        print()

    return filtered_rows, null_rows


# ---------------------------------------------------------------------------
# SKILL: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(filtered_rows: list, growth_type: str,
                   ward: str, category: str) -> list:
    """
    Computes MoM or YoY growth for each period.

    Rules:
    - Null rows get growth_rate = "NULL", formula = "N/A (null — <reason>)"
    - First valid period gets growth_rate = "N/A (first period)"
    - Every other row shows the explicit formula alongside the result
    - budgeted_amount is NEVER used
    - growth_type must be exactly "MoM" or "YoY"

    Returns:
        list[dict] — one dict per period with keys:
            period, ward, category, actual_spend, growth_rate, formula
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'."
        )

    result = []

    # Build a lookup: period -> actual_spend (float or None)
    spend_map: dict[str, float | None] = {}
    notes_map: dict[str, str] = {}
    for r in filtered_rows:
        period = r["period"]
        raw = r["actual_spend"].strip()
        spend_map[period] = float(raw) if raw != "" else None
        notes_map[period] = r["notes"].strip()

    periods = [r["period"] for r in filtered_rows]

    # For MoM: compare to the immediately preceding period in the dataset
    # For YoY: compare to the same month 12 periods earlier
    first_valid_seen = False

    for i, period in enumerate(periods):
        current_spend = spend_map[period]
        notes = notes_map[period]

        # --- NULL row ---
        if current_spend is None:
            reason = notes if notes else "no reason recorded"
            result.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_rate": "NULL",
                "formula": f"N/A (null — {reason})",
            })
            continue

        # --- Determine the reference period ---
        prev_spend = None
        prev_period = None
        prev_null_reason = None

        if growth_type == "MoM":
            if i > 0:
                prev_period = periods[i - 1]
                prev_spend = spend_map[prev_period]
                if prev_spend is None:
                    prev_null_reason = notes_map[prev_period] or "no reason recorded"
        else:  # YoY — find same month, 12 periods back
            # Parse YYYY-MM and subtract 1 year
            year, month = period.split("-")
            target_period = f"{int(year) - 1}-{month}"
            if target_period in spend_map:
                prev_period = target_period
                prev_spend = spend_map[prev_period]
                if prev_spend is None:
                    prev_null_reason = notes_map[prev_period] or "no reason recorded"

        # --- No reference period available (first period or no prior year) ---
        if prev_period is None:
            label = "first period" if not first_valid_seen else "no prior year data"
            first_valid_seen = True
            result.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_spend,
                "growth_rate": f"N/A ({label})",
                "formula": f"N/A ({label})",
            })
            continue

        first_valid_seen = True

        # --- Previous period was also null ---
        if prev_spend is None:
            result.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_spend,
                "growth_rate": "NULL (prev period also null)",
                "formula": f"N/A (prev period {prev_period} is null — {prev_null_reason})",
            })
            continue

        # --- Normal growth computation ---
        rate = (current_spend - prev_spend) / prev_spend * 100
        sign = "+" if rate >= 0 else ""
        rate_str = f"{sign}{rate:.1f}%"
        formula_str = (
            f"({current_spend} - {prev_spend}) / {prev_spend} * 100 = {rate_str}"
        )

        result.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend,
            "growth_rate": rate_str,
            "formula": formula_str,
        })

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Analyst"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        help="MoM or YoY (required)")
    parser.add_argument("--output",      required=True,  help="Output CSV filename")
    return parser.parse_args()


def main():
    args = parse_args()

    # ENFORCEMENT: growth-type must be explicit — never guess or default silently
    if not args.growth_type:
        print(
            "❌  Growth type not specified. "
            "Please pass --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(
            f"❌  Invalid --growth-type '{args.growth_type}'. "
            "Must be exactly 'MoM' or 'YoY'.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"📂  Loading: {args.input}")
    print(f"🏙️   Ward    : {args.ward}")
    print(f"📋  Category: {args.category}")
    print(f"📈  Growth  : {args.growth_type}")

    # SKILL: load_dataset (null report printed inside)
    try:
        filtered_rows, null_rows = load_dataset(args.input, args.ward, args.category)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌  {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅  {len(filtered_rows)} rows loaded ({len(null_rows)} null actual_spend).")

    # SKILL: compute_growth
    try:
        results = compute_growth(filtered_rows, args.growth_type,
                                 args.ward, args.category)
    except ValueError as e:
        print(f"❌  {e}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    output_path = Path(args.output)
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_rate", "formula"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅  Output written to: {output_path.resolve()}")
    print(f"\n{'period':<10} {'actual_spend':>14} {'growth_rate':>22}  formula")
    print("-" * 100)
    for row in results:
        print(
            f"{row['period']:<10} "
            f"{str(row['actual_spend']):>14} "
            f"{str(row['growth_rate']):>22}  "
            f"{row['formula']}"
        )


if __name__ == "__main__":
    main()

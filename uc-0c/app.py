"""
UC-0C app.py — Ward Budget Growth Calculator
Built using the RICE + agents.md + skills.md framework.
See README.md for run command and expected behaviour.

Enforcement rules implemented:
  E1 — No cross-aggregation (--ward and --category are required)
  E2 — Null-first reporting (nulls flagged before growth computation)
  E3 — Formula transparency (formula column in every output row)
  E4 — No silent formula assumption (--growth-type is required)
  E5 — Refusal over guessing (missing params → error, never guess)
"""

import argparse
import csv
import os
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(
    file_path: str, ward: str, category: str
) -> tuple[list[dict], list[dict]]:
    """
    Reads the ward budget CSV, validates columns, filters to a single
    ward + category, and reports null actual_spend rows.

    Returns:
        filtered_rows: list of dicts sorted by period, for the matching
                       ward + category.
        null_report:   list of dicts for every null actual_spend row,
                       each with {period, ward, category, reason}.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # --- Column validation ---------------------------------------------------
    required_columns = {
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    }
    actual_columns = set(rows[0].keys()) if rows else set()
    missing = required_columns - actual_columns
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    # --- Ward / category validation ------------------------------------------
    all_wards = sorted(set(r["ward"] for r in rows))
    all_categories = sorted(set(r["category"] for r in rows))

    if ward not in all_wards:
        raise ValueError(
            f"Ward '{ward}' not found in dataset. Valid wards:\n"
            + "\n".join(f"  - {w}" for w in all_wards)
        )
    if category not in all_categories:
        raise ValueError(
            f"Category '{category}' not found in dataset. Valid categories:\n"
            + "\n".join(f"  - {c}" for c in all_categories)
        )

    # --- Filter and sort -----------------------------------------------------
    filtered = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    filtered.sort(key=lambda r: r["period"])

    # --- Null report ---------------------------------------------------------
    null_report: list[dict] = []
    for r in filtered:
        spend = r.get("actual_spend", "").strip()
        if spend == "":
            null_report.append(
                {
                    "period": r["period"],
                    "ward": r["ward"],
                    "category": r["category"],
                    "reason": r.get("notes", "").strip() or "No reason provided",
                }
            )

    return filtered, null_report


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(
    filtered_rows: list[dict],
    growth_type: str,
    null_report: list[dict],
) -> list[dict]:
    """
    Computes period-over-period growth rates with full formula transparency.

    growth_type:
        MoM — month-over-month (consecutive months)
        QoQ — quarter-over-quarter (same month, previous quarter = 3 months prior)
        YoY — year-over-year (same month, previous year = 12 months prior)

    Returns a list of dicts with columns:
        period, ward, category, actual_spend, growth_rate, formula, null_flag
    """
    valid_types = {"MoM", "QoQ", "YoY"}
    if growth_type not in valid_types:
        raise ValueError(
            f"Invalid growth type '{growth_type}'. Must be one of: {sorted(valid_types)}"
        )

    if not filtered_rows:
        raise ValueError("No data found for the given ward + category combination.")

    # Build a period→spend lookup; nulls are stored as None
    null_periods = {nr["period"] for nr in null_report}
    period_spend: dict[str, Optional[float]] = {}
    for r in filtered_rows:
        period = r["period"]
        spend_str = r.get("actual_spend", "").strip()
        if spend_str == "":
            period_spend[period] = None
        else:
            period_spend[period] = float(spend_str)

    # Determine the offset for finding the prior period
    offset_map = {"MoM": 1, "QoQ": 3, "YoY": 12}
    offset = offset_map[growth_type]

    sorted_periods = sorted(period_spend.keys())

    # Build a helper to find the prior period
    def _prior_period(period_str: str, n: int) -> Optional[str]:
        """Return the period string n months before period_str, or None."""
        year, month = int(period_str[:4]), int(period_str[5:7])
        month -= n
        while month < 1:
            month += 12
            year -= 1
        candidate = f"{year:04d}-{month:02d}"
        return candidate if candidate in period_spend else None

    results: list[dict] = []
    for period in sorted_periods:
        row = filtered_rows[0]  # ward + category are the same for all
        ward = row["ward"]
        category = row["category"]
        current_spend = period_spend[period]

        # Null-flag handling
        null_flag = ""
        if current_spend is None:
            reason = next(
                (nr["reason"] for nr in null_report if nr["period"] == period),
                "No reason provided",
            )
            null_flag = f"NULL — {reason}"

        prior_key = _prior_period(period, offset)

        # Determine growth_rate and formula
        if current_spend is None:
            growth_rate = "NULL — not computed"
            formula = f"actual_spend is null for {period} ({null_flag})"
        elif prior_key is None:
            growth_rate = "N/A — no prior period"
            formula = f"No prior period available ({growth_type}, offset={offset})"
        elif period_spend.get(prior_key) is None:
            prior_reason = next(
                (nr["reason"] for nr in null_report if nr["period"] == prior_key),
                "No reason provided",
            )
            growth_rate = "NULL — not computed"
            formula = (
                f"Prior period {prior_key} actual_spend is null "
                f"({prior_reason})"
            )
        else:
            prev = period_spend[prior_key]
            cur = current_spend
            pct = (cur - prev) / prev * 100  # type: ignore[operator]
            sign = "+" if pct >= 0 else ""
            growth_rate = f"{sign}{pct:.1f}%"
            formula = (
                f"{growth_type}: ({cur} - {prev}) / {prev} * 100 = {sign}{pct:.1f}%"
            )

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_spend if current_spend is not None else "",
                "growth_rate": growth_rate,
                "formula": formula,
                "null_flag": null_flag,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Main — CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0C: Ward Budget Growth Calculator"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the ward_budget.csv file",
    )
    parser.add_argument(
        "--ward",
        required=True,
        help='Ward name (e.g., "Ward 1 – Kasba")',
    )
    parser.add_argument(
        "--category",
        required=True,
        help='Budget category (e.g., "Roads & Pothole Repair")',
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "QoQ", "YoY"],
        help="Growth calculation type: MoM, QoQ, or YoY",
    )
    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Output CSV path (default: growth_output.csv)",
    )
    args = parser.parse_args()

    # --- E5: Refusal over guessing (argparse handles required flags) ---------

    # --- E1: No cross-aggregation (ward and category are mandatory) ----------

    # --- Skill 1: load_dataset -----------------------------------------------
    print(f"Loading dataset from: {args.input}")
    print(f"Filtering — ward: {args.ward} | category: {args.category}")
    filtered_rows, null_report = load_dataset(
        args.input, args.ward, args.category
    )
    print(f"Filtered rows: {len(filtered_rows)}")

    # --- E2: Null-first reporting --------------------------------------------
    if null_report:
        print("\n⚠ Null actual_spend rows detected:")
        for nr in null_report:
            print(
                f"  • {nr['period']} | {nr['ward']} | {nr['category']} | "
                f"Reason: {nr['reason']}"
            )
        print()
    else:
        print("✓ No null actual_spend rows in the filtered data.\n")

    # --- E4: Growth type received via --growth-type (enforced by argparse) ----
    print(f"Growth type: {args.growth_type}")

    # --- Skill 2: compute_growth ---------------------------------------------
    results = compute_growth(filtered_rows, args.growth_type, null_report)

    # --- Write output CSV ----------------------------------------------------
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_rate",
        "formula",
        "null_flag",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Output written to: {args.output}")
    print(f"  Total rows: {len(results)}")

    # --- Print a summary table to stdout -------------------------------------
    print(f"\n{'Period':<10} {'Actual Spend':>14} {'Growth Rate':>20}  Formula")
    print("-" * 90)
    for r in results:
        spend_str = f"₹{r['actual_spend']} lakh" if r["actual_spend"] else "NULL"
        print(
            f"{r['period']:<10} {spend_str:>14} {r['growth_rate']:>20}  {r['formula']}"
        )


if __name__ == "__main__":
    main()

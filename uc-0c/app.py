"""
UC-0C app.py — Municipal budget growth analyst.

Enforcement rules (from agents.md):
  1. Never aggregate across wards or categories — refuse if asked.
  2. Before any computation, scan and report every null actual_spend row.
  3. Every output row must display the formula used.
  4. If --growth-type is not specified, refuse and ask — never guess.
  5. Null rows must be flagged as 'not computed' — never skipped or imputed.
"""

import argparse
import sys
import csv
from datetime import datetime

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(filepath):
    """
    Reads the ward budget CSV, validates required columns, and reports every
    null actual_spend row (with reason from notes) before returning the data.
    """
    try:
        with open(filepath, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                sys.exit(f"ERROR: '{filepath}' appears to be empty or unreadable.")

            present = {c.strip() for c in reader.fieldnames}
            missing = REQUIRED_COLUMNS - present
            if missing:
                sys.exit(
                    f"ERROR: Required column(s) missing from '{filepath}': "
                    + ", ".join(sorted(missing))
                )

            rows = []
            for row in reader:
                rows.append({k.strip(): v.strip() for k, v in row.items()})

    except FileNotFoundError:
        sys.exit(f"ERROR: Input file not found: '{filepath}'")
    except OSError as exc:
        sys.exit(f"ERROR: Cannot read '{filepath}': {exc}")

    # Build null report — do NOT drop or impute null rows
    null_report = []
    for row in rows:
        if row["actual_spend"] == "":
            reason = row["notes"] if row["notes"] else "null reason unavailable"
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": reason,
            })

    return rows, null_report


def print_null_report(null_report):
    print(f"\n=== NULL ACTUAL_SPEND REPORT ({len(null_report)} row(s)) ===")
    if not null_report:
        print("  No null values found.")
    else:
        for entry in null_report:
            print(
                f"  FLAGGED  period={entry['period']}  "
                f"ward={entry['ward']}  "
                f"category={entry['category']}  "
                f"reason={entry['reason']}"
            )
    print()


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def _prior_period(period_str, growth_type):
    """Return the prior period string for MoM or YoY."""
    dt = datetime.strptime(period_str, "%Y-%m")
    if growth_type == "MoM":
        if dt.month == 1:
            return f"{dt.year - 1}-12"
        return f"{dt.year}-{dt.month - 1:02d}"
    else:  # YoY
        return f"{dt.year - 1}-{dt.month:02d}"


def compute_growth(rows, ward, category, growth_type):
    """
    Takes a single ward, a single category, and an explicit growth_type ("MoM"
    or "YoY"). Returns a per-period table with formula shown for every row.
    """
    # Validate growth_type — never guess
    if growth_type not in ("MoM", "YoY"):
        sys.exit(
            "ERROR: --growth-type must be 'MoM' or 'YoY'. "
            "Please supply it explicitly — this tool never guesses."
        )

    # Validate ward and category exist in the dataset
    all_wards = sorted({r["ward"] for r in rows})
    all_categories = sorted({r["category"] for r in rows})

    if ward not in all_wards:
        sys.exit(
            f"ERROR: Ward '{ward}' not found in dataset.\n"
            f"  Valid wards: {', '.join(all_wards)}"
        )
    if category not in all_categories:
        sys.exit(
            f"ERROR: Category '{category}' not found in dataset.\n"
            f"  Valid categories: {', '.join(all_categories)}"
        )

    # Filter to the single ward + category — no cross-ward aggregation
    subset = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]
    if not subset:
        sys.exit(
            f"ERROR: No data found for ward='{ward}' and category='{category}'."
        )

    # Build a lookup: period -> actual_spend (float or None)
    spend_by_period = {}
    notes_by_period = {}
    for r in subset:
        raw = r["actual_spend"]
        spend_by_period[r["period"]] = float(raw) if raw != "" else None
        notes_by_period[r["period"]] = r["notes"] if r["notes"] else "null reason unavailable"

    output_rows = []
    for r in sorted(subset, key=lambda x: x["period"]):
        period = r["period"]
        current = spend_by_period[period]
        prior_period_str = _prior_period(period, growth_type)
        prior = spend_by_period.get(prior_period_str)  # None if outside dataset range

        # Determine actual_spend display value
        if current is None:
            actual_display = f"NULL — {notes_by_period[period]}"
        else:
            actual_display = current

        # Determine prior_period_spend display value
        if prior_period_str not in spend_by_period:
            prior_display = "N/A (outside dataset range)"
            formula = "N/A — no prior period in dataset"
            growth_pct = "NOT COMPUTED — no prior period"
        elif prior is None:
            prior_display = f"NULL — {notes_by_period.get(prior_period_str, 'null reason unavailable')}"
            formula = "N/A — prior period is null"
            growth_pct = "NOT COMPUTED — prior period null"
        elif current is None:
            prior_display = prior
            formula = "N/A — current period is null"
            growth_pct = "NOT COMPUTED — null value"
        else:
            prior_display = prior
            formula = f"({current} - {prior}) / {prior} × 100"
            growth_pct = round((current - prior) / prior * 100, 1)

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_display,
            "prior_period": prior_period_str,
            "prior_period_spend": prior_display,
            "formula": formula,
            "growth_pct": growth_pct,
        })

    return output_rows


def write_output(output_rows, outpath):
    fieldnames = [
        "period", "ward", "category",
        "actual_spend", "prior_period", "prior_period_spend",
        "formula", "growth_pct",
    ]
    with open(outpath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Output written to: {outpath}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Municipal budget growth analyst (per-ward, per-category)."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name (single ward only)")
    parser.add_argument("--category", required=True, help="Exact category name (single category only)")
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        default=None,
        help="Growth calculation type: MoM or YoY (required — will not be guessed)",
    )
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    # Enforcement: --growth-type must be supplied — never guessed
    if args.growth_type is None:
        parser.error(
            "--growth-type is required. Please specify 'MoM' (month-over-month) "
            "or 'YoY' (year-over-year). This tool never guesses a default."
        )

    # Skill: load_dataset — validates columns and reports nulls before any computation
    rows, null_report = load_dataset(args.input)

    print(f"Dataset loaded: {len(rows)} rows")
    print_null_report(null_report)

    # Skill: compute_growth — single ward + category only
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    write_output(output_rows, args.output)

    # Print a summary to stdout as well
    print(f"\n=== GROWTH TABLE: {args.ward} / {args.category} ({args.growth_type}) ===")
    print(f"{'Period':<10}  {'Actual Spend':>20}  {'Prior Spend':>20}  {'Growth %':>20}  Formula")
    print("-" * 110)
    for row in output_rows:
        print(
            f"{row['period']:<10}  "
            f"{str(row['actual_spend']):>20}  "
            f"{str(row['prior_period_spend']):>20}  "
            f"{str(row['growth_pct']):>20}  "
            f"{row['formula']}"
        )


if __name__ == "__main__":
    main()


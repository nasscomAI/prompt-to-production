"""
UC-0C app.py — Spend Growth Calculator
Computes month-over-month (MoM) growth for a single ward-category pair
from the ward_budget.csv dataset.

See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AGGREGATION_KEYWORDS = {"all", "any", "*", "combined", "total", "aggregate"}

REQUIRED_COLUMNS = {"period", "ward", "category",
                     "budgeted_amount", "actual_spend", "notes"}


def _to_float(value):
    """Return float or None for blank / unparseable values."""
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _is_consecutive_month(prev_period, curr_period):
    """Return True if curr_period is exactly one calendar month after prev_period."""
    try:
        py, pm = (int(x) for x in prev_period.split("-"))
        cy, cm = (int(x) for x in curr_period.split("-"))
        return (cy * 12 + cm) - (py * 12 + pm) == 1
    except (ValueError, AttributeError):
        return False


# ---------------------------------------------------------------------------
# Skill 1 — load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path):
    """
    Reads the ward budget CSV, validates columns, and reports every null
    actual_spend row (with its reason from the notes column) before
    returning the full dataset.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: Input file not found: '{file_path}'", file=sys.stderr)
        sys.exit(1)

    with open(file_path, mode="r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        headers = set(reader.fieldnames or [])

        missing = REQUIRED_COLUMNS - headers
        if missing:
            print(f"ERROR: CSV is missing required columns: {missing}",
                  file=sys.stderr)
            sys.exit(1)

        rows = list(reader)

    # Identify and report null actual_spend rows
    null_rows = [r for r in rows if r["actual_spend"].strip() == ""]

    print(f"[load_dataset] Loaded {len(rows)} rows.")
    print(f"[load_dataset] Null actual_spend rows: {len(null_rows)}")
    if null_rows:
        for nr in null_rows:
            reason = nr["notes"].strip() or "No reason provided"
            print(f"  ⚠  {nr['period']} · {nr['ward']} · "
                  f"{nr['category']} — {reason}")

    return rows


# ---------------------------------------------------------------------------
# Skill 2 — compute_growth
# ---------------------------------------------------------------------------

def compute_growth(dataset, ward, category, growth_type):
    """
    Filters the dataset for a single ward + category, then computes MoM
    growth.  Shows the formula used in every output row.  Flags null rows
    and refuses aggregation or missing growth-type.
    """

    # ── Refusal checks ────────────────────────────────────────────────
    if not growth_type:
        print("REFUSED: --growth-type was not specified. "
              "You must explicitly choose a growth type (e.g. MoM). "
              "The system will never guess.", file=sys.stderr)
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"REFUSED: Unsupported growth-type '{growth_type}'. "
              f"Only 'MoM' is currently supported.", file=sys.stderr)
        sys.exit(1)

    if not ward or ward.strip().lower() in AGGREGATION_KEYWORDS:
        print("REFUSED: --ward is missing or set to an aggregation keyword. "
              "This system never aggregates across wards.", file=sys.stderr)
        sys.exit(1)

    if not category or category.strip().lower() in AGGREGATION_KEYWORDS:
        print("REFUSED: --category is missing or set to an aggregation keyword. "
              "This system never aggregates across categories.", file=sys.stderr)
        sys.exit(1)

    # ── Filter & sort ─────────────────────────────────────────────────
    filtered = [
        r for r in dataset
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', "
              f"category='{category}'.", file=sys.stderr)
        sys.exit(1)

    filtered.sort(key=lambda r: r["period"])

    # ── Compute MoM growth per period ─────────────────────────────────
    results = []

    for idx, row in enumerate(filtered):
        period = row["period"]
        spend = _to_float(row["actual_spend"])
        note = row["notes"].strip()

        # Current month is null → flag it, do not compute
        if spend is None:
            results.append({
                "Ward": row["ward"],
                "Category": row["category"],
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "MoM Growth": f"NULL — Flagged: {note or 'no reason'}",
                "Formula": "N/A — actual_spend is null",
            })
            continue

        spend_display = str(spend)

        # First month → no previous month to compare against
        if idx == 0:
            results.append({
                "Ward": row["ward"],
                "Category": row["category"],
                "Period": period,
                "Actual Spend (₹ lakh)": spend_display,
                "MoM Growth": "N/A (first month)",
                "Formula": "N/A",
            })
            continue

        prev = filtered[idx - 1]
        prev_spend = _to_float(prev["actual_spend"])

        # Non-consecutive month
        if not _is_consecutive_month(prev["period"], period):
            results.append({
                "Ward": row["ward"],
                "Category": row["category"],
                "Period": period,
                "Actual Spend (₹ lakh)": spend_display,
                "MoM Growth": f"NULL — non-consecutive (prev: {prev['period']})",
                "Formula": "N/A",
            })
            continue

        # Previous month was null → cannot compute
        if prev_spend is None:
            results.append({
                "Ward": row["ward"],
                "Category": row["category"],
                "Period": period,
                "Actual Spend (₹ lakh)": spend_display,
                "MoM Growth": "NULL — previous month actual_spend is null",
                "Formula": f"({spend} − NULL) / NULL",
            })
            continue

        # Normal MoM calculation
        growth = (spend - prev_spend) / prev_spend
        pct = growth * 100

        if pct > 0:
            growth_str = f"+{pct:.1f}%"
        elif pct < 0:
            growth_str = f"{pct:.1f}%"          # negative sign included
        else:
            growth_str = "0.0%"

        results.append({
            "Ward": row["ward"],
            "Category": row["category"],
            "Period": period,
            "Actual Spend (₹ lakh)": spend_display,
            "MoM Growth": growth_str,
            "Formula": f"({spend} − {prev_spend}) / {prev_spend}",
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Spend Growth Calculator")
    parser.add_argument("--input",  required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward",   default=None,
                        help="Exact ward name (required)")
    parser.add_argument("--category", default=None,
                        help="Exact category name (required)")
    parser.add_argument("--growth-type", default=None,
                        help="Growth type, e.g. MoM (required)")
    parser.add_argument("--output", required=True,
                        help="Path for the output CSV")
    args = parser.parse_args()

    # ── Enforcement: refuse before any work if parameters are missing ──
    if args.growth_type is None:
        print("REFUSED: --growth-type was not specified. "
              "You must explicitly choose a growth type (e.g. MoM). "
              "The system will never guess.", file=sys.stderr)
        sys.exit(1)

    if args.ward is None or args.ward.strip() == "":
        print("REFUSED: --ward was not specified. "
              "Aggregation across all wards is prohibited.",
              file=sys.stderr)
        sys.exit(1)

    if args.category is None or args.category.strip() == "":
        print("REFUSED: --category was not specified. "
              "Aggregation across all categories is prohibited.",
              file=sys.stderr)
        sys.exit(1)

    # ── Skill 1: load_dataset ─────────────────────────────────────────
    dataset = load_dataset(args.input)

    # ── Skill 2: compute_growth ───────────────────────────────────────
    results = compute_growth(dataset, args.ward, args.category,
                             args.growth_type)

    # ── Write output CSV ──────────────────────────────────────────────
    fieldnames = ["Ward", "Category", "Period",
                  "Actual Spend (₹ lakh)", "MoM Growth", "Formula"]

    with open(args.output, mode="w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Output written to '{args.output}' "
          f"({len(results)} rows).")


if __name__ == "__main__":
    main()

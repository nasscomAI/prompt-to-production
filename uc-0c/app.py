"""
UC-0C app.py — Budget Growth Calculator
Computes per-period growth rates for a single ward and category,
flagging null rows and showing formulas. Never aggregates across wards.

Built using agents.md (enforcement rules) and skills.md (skill definitions).
"""
import argparse
import csv
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(file_path: str) -> tuple:
    """
    Read budget CSV, validate columns, report nulls.
    Returns: (rows list, null_rows list)
    """
    path = Path(file_path)

    if not path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate columns
        if reader.fieldnames is None:
            print("ERROR: Could not read CSV headers.", file=sys.stderr)
            sys.exit(1)

        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

        for row in reader:
            rows.append(row)

    if not rows:
        print(f"ERROR: No data rows in {file_path}", file=sys.stderr)
        sys.exit(1)

    # Identify null actual_spend rows
    null_rows = []
    for row in rows:
        if not row["actual_spend"] or row["actual_spend"].strip() == "":
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided"),
            })

    # Report
    wards = sorted(set(r["ward"] for r in rows))
    categories = sorted(set(r["category"] for r in rows))
    print(f"  Total rows: {len(rows)}")
    print(f"  Wards: {len(wards)} — {', '.join(wards)}")
    print(f"  Categories: {len(categories)} — {', '.join(categories)}")
    print(f"  Null actual_spend rows: {len(null_rows)}")

    if null_rows:
        print("  NULL ROW DETAILS:")
        for nr in null_rows:
            print(f"    - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    return rows, null_rows


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for a single ward + category.
    Returns list of result dicts with formula shown.
    """
    # Validate growth_type
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth-type '{growth_type}'. Must be 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    # Filter rows for specified ward + category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        all_wards = sorted(set(r["ward"] for r in rows))
        all_cats = sorted(set(r["category"] for r in rows))
        print(f"ERROR: No rows found for ward='{ward}', category='{category}'", file=sys.stderr)
        print(f"  Available wards: {all_wards}", file=sys.stderr)
        print(f"  Available categories: {all_cats}", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Compute growth
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip() if row["actual_spend"] else ""
        notes = row.get("notes", "")

        # Check if current row is null
        if not actual_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_period": "",
                "previous_spend": "",
                "growth_pct": "",
                "formula": "",
                "flag": f"NULL — {notes.strip() if notes.strip() else 'No reason provided'}",
            })
            continue

        actual = float(actual_str)

        # Determine previous period index based on growth type
        if growth_type == "MoM":
            prev_idx = i - 1
        else:  # YoY
            # Find same month in previous year
            prev_idx = i - 12 if i >= 12 else -1

        # First period or no previous available
        if prev_idx < 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual}",
                "previous_period": "",
                "previous_spend": "",
                "growth_pct": "N/A",
                "formula": "N/A — no previous period",
                "flag": "",
            })
            continue

        # Check if previous period is null
        prev_row = filtered[prev_idx]
        prev_actual_str = prev_row["actual_spend"].strip() if prev_row["actual_spend"] else ""

        if not prev_actual_str:
            prev_notes = prev_row.get("notes", "")
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual}",
                "previous_period": prev_row["period"],
                "previous_spend": "NULL",
                "growth_pct": "",
                "formula": "",
                "flag": f"Cannot compute — previous period ({prev_row['period']}) is NULL: {prev_notes.strip()}",
            })
            continue

        # Compute growth
        prev_actual = float(prev_actual_str)
        if prev_actual == 0:
            growth_pct = "INF"
            formula = f"({actual} - 0) / 0 * 100 = undefined (division by zero)"
            flag = "Division by zero — previous spend is 0"
        else:
            growth = ((actual - prev_actual) / prev_actual) * 100
            growth_pct = f"{growth:+.1f}%"
            formula = f"({actual} - {prev_actual}) / {prev_actual} * 100 = {growth:+.1f}%"
            flag = ""

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual}",
            "previous_period": prev_row["period"],
            "previous_spend": f"{prev_actual}",
            "growth_pct": growth_pct,
            "formula": formula,
            "flag": flag,
        })

    return results


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Budget growth calculator — single ward, single category"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth calculation type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path for output CSV")
    args = parser.parse_args()

    # Enforcement: refuse if ward/category/growth-type not specified
    # (argparse handles this with required=True)

    print(f"Loading dataset: {args.input}")
    rows, null_rows = load_dataset(args.input)

    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output CSV
    output_fields = ["period", "ward", "category", "actual_spend", "previous_period",
                     "previous_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nOutput written to: {args.output}")
    print(f"  Total periods: {len(results)}")
    flagged = [r for r in results if r["flag"]]
    if flagged:
        print(f"  Flagged rows: {len(flagged)}")
        for fr in flagged:
            print(f"    - {fr['period']}: {fr['flag']}")


if __name__ == "__main__":
    main()

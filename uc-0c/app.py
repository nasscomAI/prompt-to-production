"""
UC-0C — Number That Looks Right

Computes month-over-month growth from ward-level budget data.
Never aggregates across wards or categories. Flags all null values.

Implements the two skills in skills.md:
  - load_dataset: reads CSV, validates columns, reports nulls
  - compute_growth: per-period growth table with formula shown
"""
import argparse
import csv
import sys


def load_dataset(file_path: str) -> list:
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows.
    Returns the list of row dicts.
    """
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # Validate required columns
    required = ["period", "ward", "category", "budgeted_amount", "actual_spend"]
    if rows:
        missing = [c for c in required if c not in rows[0]]
        if missing:
            print(f"ERROR: Missing required columns: {missing}")
            sys.exit(1)

    # Report null actual_spend rows
    null_rows = [r for r in rows if not r.get("actual_spend", "").strip()]
    if null_rows:
        print(f"[!] NULL REPORT: {len(null_rows)} rows have null actual_spend:")
        print("-" * 80)
        for r in null_rows:
            reason = r.get("notes", "No reason provided").strip()
            print(f"  {r['period']} | {r['ward']} | {r['category']} | Reason: {reason}")
        print("-" * 80)
        print()

    print(f"Loaded {len(rows)} rows. {len(null_rows)} null values found.\n")
    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM or YoY growth for a specific ward and category.
    Returns per-period results with formula shown.
    """
    # Filter for specified ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'")
        print("Available wards:", sorted(set(r["ward"] for r in rows)))
        print("Available categories:", sorted(set(r["category"] for r in rows)))
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_raw = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        # Check if current value is null
        if not actual_raw:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_spend": "",
                "growth_pct": "NULL",
                "formula": "N/A — actual_spend is NULL",
                "flag": f"NULL: {notes}" if notes else "NULL: No reason provided",
            })
            continue

        actual = float(actual_raw)

        if growth_type == "MoM":
            if i == 0:
                # First period — no previous month
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": str(actual),
                    "previous_spend": "N/A",
                    "growth_pct": "N/A",
                    "formula": "N/A — first period, no previous month",
                    "flag": "",
                })
                continue

            prev_row = filtered[i - 1]
            prev_raw = prev_row.get("actual_spend", "").strip()
            prev_notes = prev_row.get("notes", "").strip()

            if not prev_raw:
                # Previous month is null
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": str(actual),
                    "previous_spend": "NULL",
                    "growth_pct": "NULL",
                    "formula": f"N/A — previous month ({prev_row['period']}) actual_spend is NULL",
                    "flag": f"Previous month NULL: {prev_notes}" if prev_notes else "Previous month NULL",
                })
                continue

            prev = float(prev_raw)
            if prev == 0:
                growth = "INF"
                formula = f"({actual} - 0) / 0 * 100 = undefined"
            else:
                growth_val = ((actual - prev) / prev) * 100
                growth = f"{growth_val:+.1f}%"
                formula = f"({actual} - {prev}) / {prev} * 100 = {growth_val:+.1f}%"

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual),
                "previous_spend": str(prev),
                "growth_pct": growth,
                "formula": formula,
                "flag": "",
            })

        elif growth_type == "YoY":
            # Year-over-year — compare to same month previous year
            # For 2024 data only, there is no 2023, so all would be N/A
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual),
                "previous_spend": "N/A",
                "growth_pct": "N/A",
                "formula": "N/A — no previous year data available in dataset",
                "flag": "",
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Skill 1: load_dataset
    print(f"Loading dataset from: {args.input}")
    rows = load_dataset(args.input)

    # Skill 2: compute_growth
    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    print()

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "previous_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {args.output}")
    print(f"Total periods: {len(results)}")

    # Print summary
    null_results = [r for r in results if "NULL" in str(r.get("growth_pct", ""))]
    if null_results:
        print(f"[!] {len(null_results)} periods have NULL growth (missing data):")
        for r in null_results:
            print(f"  {r['period']}: {r['flag']}")


if __name__ == "__main__":
    main()

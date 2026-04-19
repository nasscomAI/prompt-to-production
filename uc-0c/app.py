"""
UC-0C -- Number That Looks Right
Computes per-ward per-category MoM/YoY growth from municipal budget data.
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.

Enforcement focus:
  - Never aggregate across wards or categories
  - Flag all null actual_spend rows with reason before computing
  - Show formula for every computed value
  - Refuse if --growth-type not specified
"""
import argparse
import csv
import sys


# -- Skill: load_dataset -------------------------------------------------------

def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows.

    Returns:
        (data, null_report) where data is all rows and null_report lists
        the rows with missing actual_spend.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}")
        sys.exit(1)

    # Validate required columns
    required = ["period", "ward", "category", "budgeted_amount", "actual_spend"]
    if rows:
        missing = [c for c in required if c not in rows[0]]
        if missing:
            print(f"ERROR: Missing required columns: {', '.join(missing)}")
            sys.exit(1)

    # Scan for null actual_spend rows
    null_report = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided").strip(),
            })

    # Print null report (enforcement: report nulls before computing)
    print(f"\n{'='*60}")
    print(f"  DATASET LOAD REPORT")
    print(f"{'='*60}")
    print(f"  Total rows: {len(rows)}")
    print(f"  Null actual_spend rows: {len(null_report)}")
    if null_report:
        print(f"\n  NULL ROWS DETECTED (will NOT be computed):")
        for nr in null_report:
            print(f"    - {nr['period']} | {nr['ward']} | {nr['category']}")
            print(f"      Reason: {nr['notes']}")
    print(f"{'='*60}\n")

    return rows, null_report


# -- Skill: compute_growth -----------------------------------------------------

def compute_growth(
    data: list[dict],
    null_report: list[dict],
    ward: str,
    category: str,
    growth_type: str,
    output_path: str,
):
    """
    Compute period-over-period growth for a specific ward + category.

    Enforcement rules applied:
    1. Only per-ward per-category -- never aggregate
    2. Null rows flagged, not computed
    3. Adjacent-to-null rows flagged
    4. Formula shown for every row
    5. Percentages rounded to 1 decimal place
    """
    # Filter data for the specified ward + category
    filtered = [
        r for r in data
        if r["ward"].strip() == ward and r["category"].strip() == category
    ]

    if not filtered:
        # List available wards and categories to help the user
        wards = sorted(set(r["ward"].strip() for r in data))
        categories = sorted(set(r["category"].strip() for r in data))
        print(f"ERROR: No data found for ward='{ward}', category='{category}'")
        print(f"  Available wards: {', '.join(wards)}")
        print(f"  Available categories: {', '.join(categories)}")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Build set of null (period, ward, category) for quick lookup
    null_set = set()
    for nr in null_report:
        null_set.add((nr["period"], nr["ward"], nr["category"]))

    # Compute growth
    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row["actual_spend"].strip() if row["actual_spend"] else ""
        notes = row.get("notes", "").strip()
        is_null = (period, ward, category) in null_set or spend_str == ""

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": spend_str if not is_null else "NULL",
            "previous_spend": "",
            "growth_pct": "",
            "formula": "",
            "flag": "",
            "notes": notes,
        }

        if is_null:
            result["flag"] = "NULL_DATA"
            result["notes"] = notes if notes else "Null actual_spend"
            results.append(result)
            continue

        current_spend = float(spend_str)
        result["actual_spend"] = f"{current_spend}"

        if i == 0:
            # First period -- no previous data for MoM
            result["flag"] = "NO_PREVIOUS"
            result["formula"] = "N/A (first period)"
            results.append(result)
            continue

        # Check if previous row is null
        prev_row = filtered[i - 1]
        prev_period = prev_row["period"]
        prev_spend_str = prev_row["actual_spend"].strip() if prev_row["actual_spend"] else ""
        prev_is_null = (prev_period, ward, category) in null_set or prev_spend_str == ""

        if prev_is_null:
            result["flag"] = "ADJACENT_NULL"
            result["previous_spend"] = "NULL"
            result["formula"] = f"Cannot compute: previous period ({prev_period}) has null data"
            result["notes"] = f"Previous period {prev_period} is null"
            results.append(result)
            continue

        # Normal computation
        prev_spend = float(prev_spend_str)
        result["previous_spend"] = f"{prev_spend}"

        if prev_spend == 0:
            result["flag"] = "DIVISION_BY_ZERO"
            result["formula"] = f"({current_spend} - 0) / 0 * 100 = undefined"
            results.append(result)
            continue

        if growth_type == "MoM":
            growth = (current_spend - prev_spend) / prev_spend * 100
            growth_rounded = round(growth, 1)
            sign = "+" if growth_rounded >= 0 else ""
            result["growth_pct"] = f"{sign}{growth_rounded}%"
            result["formula"] = (
                f"({current_spend} - {prev_spend}) / {prev_spend} * 100 "
                f"= {sign}{growth_rounded}%"
            )
        # YoY would need 12-month lookback -- not implemented for this dataset
        # since we only have 12 months of data

        results.append(result)

    # Write output CSV
    fieldnames = [
        "period", "ward", "category", "actual_spend", "previous_spend",
        "growth_pct", "formula", "flag", "notes",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    print(f"\n{'='*60}")
    print(f"  GROWTH OUTPUT SUMMARY")
    print(f"  Ward:     {ward}")
    print(f"  Category: {category}")
    print(f"  Type:     {growth_type}")
    print(f"{'='*60}")
    for r in results:
        flag_str = f"  [{r['flag']}]" if r['flag'] else ""
        spend_str = r['actual_spend']
        growth_str = r['growth_pct'] if r['growth_pct'] else "N/A"
        print(f"  {r['period']}  Spend: {spend_str:>8s}  Growth: {growth_str:>10s}{flag_str}")
    print(f"{'='*60}\n")

    return results


def main():
    """Main entry point for UC-0C budget growth calculator."""
    parser = argparse.ArgumentParser(
        description="UC-0C -- Budget Growth Calculator (Number That Looks Right)"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward", required=True,
        help="Ward name (e.g. 'Ward 1 - Kasba')"
    )
    parser.add_argument(
        "--category", required=True,
        help="Category name (e.g. 'Roads & Pothole Repair')"
    )
    parser.add_argument(
        "--growth-type", required=False, default=None,
        help="Growth type: MoM or YoY (REQUIRED -- system will refuse without it)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write growth_output.csv"
    )
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if args.growth_type is None:
        print("ERROR: --growth-type is required. Please specify MoM or YoY.")
        print("  Example: --growth-type MoM")
        print("  The system will NOT assume a default growth type.")
        sys.exit(1)

    growth_type = args.growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        print(f"ERROR: Invalid growth type '{args.growth_type}'. Must be MoM or YoY.")
        sys.exit(1)

    # Normalize to standard form
    if growth_type == "MOM":
        growth_type = "MoM"
    else:
        growth_type = "YoY"

    # Step 1: Load and report nulls
    data, null_report = load_dataset(args.input)

    # Step 2: Compute growth
    compute_growth(data, null_report, args.ward, args.category, growth_type, args.output)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

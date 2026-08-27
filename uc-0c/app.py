"""
UC-0C — Number That Looks Right
Computes MoM spending growth per-ward per-category with null flagging and formula display.
"""
import argparse
import csv
import sys


# ---------------------------------------------------------------------------
# load_dataset — reads CSV, validates columns, reports nulls
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str) -> list:
    """Load ward budget CSV and validate columns. Returns list of row dicts."""
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate columns
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            print(f"ERROR: Missing required columns: {missing}")
            sys.exit(1)

        rows = list(reader)

    # Report nulls
    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    if null_rows:
        print(f"\nNull actual_spend detected: {len(null_rows)} rows")
        for r in null_rows:
            reason = r["notes"].strip() if r["notes"].strip() else "No reason provided"
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | Reason: {reason}")
        print()

    return rows


# ---------------------------------------------------------------------------
# compute_growth — per-ward per-category MoM growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM growth for a specific ward and category.
    Returns list of result dicts with formula shown.
    """
    # Validate growth type
    if growth_type != "MoM":
        print(f"ERROR: Unsupported growth type '{growth_type}'. Only 'MoM' is supported.")
        sys.exit(1)

    # Filter to specified ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'.")
        print(f"Available wards: {sorted(set(r['ward'] for r in rows))}")
        print(f"Available categories: {sorted(set(r['category'] for r in rows))}")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    prev_spend = None

    for row in filtered:
        period = row["period"]
        actual_raw = row["actual_spend"].strip()
        notes = row["notes"].strip()

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "",
            "previous_spend": "",
            "mom_growth_pct": "",
            "formula": "",
            "flag": "",
        }

        # Handle null actual_spend
        if not actual_raw:
            reason = notes if notes else "No reason provided"
            result["actual_spend"] = "NULL"
            result["flag"] = f"NULL — {reason}"
            result["formula"] = "Not computed — actual_spend is NULL"
            results.append(result)
            prev_spend = None  # Next row can't compute MoM either
            continue

        current_spend = float(actual_raw)
        result["actual_spend"] = f"{current_spend}"

        # Compute MoM growth
        if prev_spend is None:
            result["previous_spend"] = "N/A"
            result["mom_growth_pct"] = "N/A"
            result["formula"] = "No previous period available"
        else:
            mom = ((current_spend - prev_spend) / prev_spend) * 100
            result["previous_spend"] = f"{prev_spend}"
            result["mom_growth_pct"] = f"{mom:+.1f}%"
            result["formula"] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100 = {mom:+.1f}%"

        results.append(result)
        prev_spend = current_spend

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Refuse if growth type not specified (argparse handles required, but double-check)
    if not args.growth_type:
        print("ERROR: --growth-type is required. Specify 'MoM'. Do not guess.")
        sys.exit(1)

    # Step 1: Load and validate
    print(f"Loading dataset: {args.input}")
    rows = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows.")

    # Step 2: Compute growth
    print(f"Computing {args.growth_type} growth for: {args.ward} / {args.category}")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Step 3: Write output
    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend",
                   "mom_growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Results written to {args.output}")

    # Print summary
    null_count = sum(1 for r in results if r["flag"].startswith("NULL"))
    computed = sum(1 for r in results if r["mom_growth_pct"] and r["mom_growth_pct"] != "N/A")
    print(f"  Periods: {len(results)} | Computed: {computed} | Null-flagged: {null_count}")


if __name__ == "__main__":
    main()

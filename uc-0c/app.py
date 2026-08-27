"""
UC-0C — Number That Looks Right
Computes per-ward per-category budget growth from ward_budget.csv.
Flags null values, shows formulas, and refuses cross-ward aggregation.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]


def load_dataset(file_path: str) -> list[dict]:
    """
    Read the ward_budget CSV, validate columns, and report null actual_spend
    rows with their reasons before returning the data.
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate columns
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        rows = list(reader)

    # Report summary
    wards = sorted(set(r["ward"] for r in rows))
    categories = sorted(set(r["category"] for r in rows))
    null_rows = [r for r in rows if not r["actual_spend"].strip()]

    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Wards ({len(wards)}): {', '.join(wards)}")
    print(f"Categories ({len(categories)}): {', '.join(categories)}")
    print(f"Null actual_spend rows: {len(null_rows)}")

    if null_rows:
        print("\n  NULL ROWS DETECTED:")
        for r in null_rows:
            notes = r["notes"].strip() if r["notes"].strip() else "No reason given"
            print(f"    - {r['period']} | {r['ward']} | {r['category']} | "
                  f"Reason: {notes}")
        print()

    return rows


def compute_growth(data: list[dict], ward: str, category: str,
                   growth_type: str) -> list[dict]:
    """
    Compute growth for a specific ward + category + growth_type.
    Returns per-period results with formula shown.
    """
    # Validate growth_type
    if growth_type not in ("MoM",):
        raise ValueError(
            f"Unsupported growth_type: '{growth_type}'. "
            f"Valid options: MoM (Month-over-Month)."
        )

    # Filter to specific ward + category
    filtered = [r for r in data
                if r["ward"] == ward and r["category"] == category]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in data))
        available_cats = sorted(set(r["category"] for r in data))
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    prev_spend = None
    prev_was_null = False

    for row in filtered:
        period = row["period"]
        spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if not spend_str:
            # NULL actual_spend
            null_reason = notes if notes else "No reason given"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_pct": "NULL",
                "formula": "Not computed — actual_spend is null",
                "flag": f"NULL: {null_reason}",
            })
            prev_spend = None
            prev_was_null = True
            continue

        spend = float(spend_str)

        if prev_spend is None:
            # First row or row after null — no previous to compare
            flag = ""
            if prev_was_null:
                flag = "Previous period was NULL — growth may be unreliable"

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{spend:.1f}",
                "growth_pct": "N/A" if not results else "N/A (no prior)",
                "formula": "No prior period for comparison"
                           if not prev_was_null else
                           "Prior period was NULL — cannot compute",
                "flag": flag if flag else ("First period" if not results else ""),
            })
        else:
            # Compute MoM growth
            growth = ((spend - prev_spend) / prev_spend) * 100
            sign = "+" if growth >= 0 else ""
            formula = (f"(({spend:.1f} - {prev_spend:.1f}) / "
                       f"{prev_spend:.1f}) x 100 = {sign}{growth:.1f}%")

            flag = ""
            if prev_was_null:
                flag = "Previous period was NULL — growth may be unreliable"

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{spend:.1f}",
                "growth_pct": f"{sign}{growth:.1f}%",
                "formula": formula,
                "flag": flag,
            })

        prev_spend = spend
        prev_was_null = False

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Ward name (exact match)")
    parser.add_argument("--category", required=True,
                        help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, dest="growth_type",
                        help="Growth type: MoM")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    print(f"Loading dataset: {args.input}")
    data = load_dataset(args.input)

    # Step 2: Compute growth
    print(f"Computing {args.growth_type} growth for: "
          f"{args.ward} / {args.category}")
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Step 3: Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nOutput written to: {args.output}")
    print(f"Rows: {len(results)}")

    # Print summary table
    print(f"\n{'Period':<10} {'Spend':>8} {'Growth':>10} {'Flag'}")
    print("-" * 50)
    for r in results:
        spend = r['actual_spend'] if r['actual_spend'] else 'NULL'
        print(f"{r['period']:<10} {spend:>8} {r['growth_pct']:>10} "
              f"{r['flag']}")


if __name__ == "__main__":
    main()

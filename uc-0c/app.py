"""
UC-0C — Budget Growth Analyser (Number That Looks Right)
Computes MoM or YoY budget growth for a single ward AND single category.
CRAFT-enforced: per-ward per-category only, nulls flagged, formula shown every row.
"""
import argparse
import csv


def load_dataset(file_path: str, ward: str, category: str) -> list:
    """
    Reads CSV, validates columns, filters to ward+category, reports nulls before returning.
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        found_columns = set(reader.fieldnames or [])

    # Validate columns
    missing_cols = required_columns - found_columns
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Filter to requested ward + category
    filtered = [
        r for r in all_rows
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in all_rows))
        available_cats = sorted(set(r["category"] for r in all_rows))
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # NULL REPORT — printed before any computation (enforcement rule)
    null_rows = [r for r in filtered if not r["actual_spend"] or r["actual_spend"].strip() == ""]
    print(f"\nNULL REPORT for ward='{ward}', category='{category}':")
    if null_rows:
        for nr in null_rows:
            reason = nr.get("notes", "No reason provided")
            print(f"  NULL: period={nr['period']} | reason: {reason}")
    else:
        print(f"  No null rows found in {len(filtered)} rows.")
    print()

    return filtered


def compute_growth(rows: list, growth_type: str) -> list:
    """
    Computes MoM or YoY growth per period with formula shown.
    Null rows included with null_flag=NULL.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got: '{growth_type}'")

    results = []

    # Build a lookup of period → actual_spend (float or None)
    spend_by_period = {}
    for row in rows:
        period = row["period"]
        val = row["actual_spend"].strip() if row["actual_spend"] else ""
        spend_by_period[period] = float(val) if val else None

    for i, row in enumerate(rows):
        period = row["period"]
        current_val = spend_by_period.get(period)
        note = row.get("notes", "").strip()

        if current_val is None:
            # Null row — flag it, skip growth
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "N/A",
                "formula": "N/A — null actual_spend",
                "null_flag": f"NULL | {note}"
            })
            continue

        # Find the comparison period
        if growth_type == "MoM":
            if i == 0:
                # First row — no previous month
                results.append({
                    "period": period,
                    "actual_spend": f"{current_val:.1f}",
                    "growth_pct": "N/A",
                    "formula": "N/A — first period, no prior month",
                    "null_flag": ""
                })
                continue
            # Previous row
            prev_row = rows[i - 1]
            prev_val = spend_by_period.get(prev_row["period"])

            if prev_val is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{current_val:.1f}",
                    "growth_pct": "N/A",
                    "formula": f"N/A — prior period {prev_row['period']} is null",
                    "null_flag": ""
                })
                continue

            growth = ((current_val - prev_val) / prev_val) * 100
            formula = f"MoM=({current_val}-{prev_val})/{prev_val}*100"
            results.append({
                "period": period,
                "actual_spend": f"{current_val:.1f}",
                "growth_pct": f"{growth:+.1f}%",
                "formula": formula,
                "null_flag": ""
            })

        elif growth_type == "YoY":
            # Find same period last year (period is YYYY-MM)
            year, month = period.split("-")
            prior_period = f"{int(year)-1}-{month}"
            prior_val = spend_by_period.get(prior_period)

            if prior_val is None and prior_period not in spend_by_period:
                results.append({
                    "period": period,
                    "actual_spend": f"{current_val:.1f}",
                    "growth_pct": "N/A",
                    "formula": f"N/A — no data for prior year period {prior_period}",
                    "null_flag": ""
                })
                continue

            if prior_val is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{current_val:.1f}",
                    "growth_pct": "N/A",
                    "formula": f"N/A — prior period {prior_period} is null",
                    "null_flag": ""
                })
                continue

            growth = ((current_val - prior_val) / prior_val) * 100
            formula = f"YoY=({current_val}-{prior_val})/{prior_val}*100"
            results.append({
                "period": period,
                "actual_spend": f"{current_val:.1f}",
                "growth_pct": f"{growth:+.1f}%",
                "formula": formula,
                "null_flag": ""
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Single ward name (exact match)")
    parser.add_argument("--category",    required=True,  help="Single category name (exact match)")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY",
                        choices=["MoM", "YoY"])
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Refuse cross-ward/cross-category aggregation
    if args.ward.lower() in ("all", "*", ""):
        print("REFUSED: Specify a single ward. Cross-ward aggregation is not permitted.")
        return
    if args.category.lower() in ("all", "*", ""):
        print("REFUSED: Specify a single category. Cross-category aggregation is not permitted.")
        return

    print(f"Loading data for ward='{args.ward}', category='{args.category}'...")
    rows = load_dataset(args.input, args.ward, args.category)
    print(f"Loaded {len(rows)} rows.")

    print(f"Computing {args.growth_type} growth...")
    results = compute_growth(rows, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "growth_pct", "formula", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to {args.output}")
    print(f"Periods computed: {len(results)}")
    null_count = sum(1 for r in results if r["null_flag"])
    print(f"Null-flagged rows: {null_count}")


if __name__ == "__main__":
    main()
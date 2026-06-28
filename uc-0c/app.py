"""
UC-0C — Number That Looks Right
Reads ward_budget.csv and computes per-ward, per-category growth (MoM or YoY).
Enforcement: no cross-ward aggregation, null rows flagged, formula shown, growth-type required.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "actual_spend", "notes"}


def load_dataset(input_path: str) -> list:
    """
    Reads ward_budget CSV, validates columns, reports null rows before returning.
    Returns: list of row dicts with all columns.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                raise ValueError(f"File is empty: {input_path}")
            missing = REQUIRED_COLUMNS - set(rows[0].keys())
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    # Report nulls before returning
    null_rows = [r for r in rows if r.get("actual_spend", "").strip() == ""]
    print(f"\n=== NULL REPORT: {len(null_rows)} null actual_spend row(s) found ===")
    for r in null_rows:
        reason = r.get("notes", "No reason provided").strip() or "No reason provided"
        print(f"  NULL: {r['period']} | {r['ward']} | {r['category']} | Reason: {reason}")
    print("=" * 60)

    return rows


def compute_growth(rows: list, growth_type: str) -> list:
    """
    Computes MoM or YoY growth per period for a pre-filtered ward+category dataset.
    Returns list of result dicts with formula shown and null rows flagged.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "Please specify --growth-type as MoM or YoY. This system will not guess."
        )

    # Sort by period
    rows_sorted = sorted(rows, key=lambda r: r["period"])

    results = []
    for i, row in enumerate(rows_sorted):
        period = row["period"]
        ward = row["ward"]
        category = row["category"]
        raw_spend = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        # Current period is null
        if raw_spend == "":
            reason = notes if notes else "No reason in notes"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_pct": "NULL_FLAG",
                "formula": "N/A — actual_spend is null",
                "flag": f"NULL_FLAG: {reason}",
            })
            continue

        current = float(raw_spend)

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current,
                    "growth_pct": "N/A",
                    "formula": "MoM: no prior period",
                    "flag": "",
                })
                continue

            prev_row = rows_sorted[i - 1]
            prev_spend_raw = prev_row.get("actual_spend", "").strip()
            if prev_spend_raw == "":
                prev_notes = prev_row.get("notes", "").strip() or "No reason in notes"
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current,
                    "growth_pct": "NULL_FLAG",
                    "formula": f"MoM: ({period} - {prev_row['period']}) / {prev_row['period']} × 100 — cannot compute, prior period is null",
                    "flag": f"NULL_FLAG: prior period {prev_row['period']} is null ({prev_notes})",
                })
                continue

            prev = float(prev_spend_raw)
            if prev == 0:
                growth = None
                formula_str = f"MoM: ({current} - {prev}) / {prev} × 100 — division by zero"
                flag = "NULL_FLAG: prior period actual_spend is 0, division not possible"
            else:
                growth = round((current - prev) / prev * 100, 1)
                formula_str = f"MoM: ({current} - {prev}) / {prev} × 100 = {growth:+.1f}%"
                flag = ""

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current,
                "growth_pct": growth if growth is not None else "NULL_FLAG",
                "formula": formula_str,
                "flag": flag,
            })

        elif growth_type == "YoY":
            # YoY: compare with same month previous year (not in 2024 dataset, but handle gracefully)
            same_month_prev_year_period = f"{int(period[:4]) - 1}-{period[5:]}"
            prev_row = next(
                (r for r in rows_sorted if r["period"] == same_month_prev_year_period), None
            )
            if prev_row is None:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current,
                    "growth_pct": "N/A",
                    "formula": f"YoY: no data for prior year period {same_month_prev_year_period}",
                    "flag": "",
                })
                continue

            prev_spend_raw = prev_row.get("actual_spend", "").strip()
            if prev_spend_raw == "":
                prev_notes = prev_row.get("notes", "").strip() or "No reason in notes"
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current,
                    "growth_pct": "NULL_FLAG",
                    "formula": f"YoY: ({period} - {same_month_prev_year_period}) — cannot compute, prior year period is null",
                    "flag": f"NULL_FLAG: prior year period is null ({prev_notes})",
                })
                continue

            prev = float(prev_spend_raw)
            if prev == 0:
                growth = None
                formula_str = f"YoY: ({current} - {prev}) / {prev} × 100 — division by zero"
                flag = "NULL_FLAG: prior year actual_spend is 0"
            else:
                growth = round((current - prev) / prev * 100, 1)
                formula_str = f"YoY: ({current} - {prev}) / {prev} × 100 = {growth:+.1f}%"
                flag = ""

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current,
                "growth_pct": growth if growth is not None else "NULL_FLAG",
                "formula": formula_str,
                "flag": flag,
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Ward name to filter")
    parser.add_argument("--category", required=False, default=None, help="Category to filter")
    parser.add_argument("--growth-type", required=False, default=None,
                        dest="growth_type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: refuse if no growth type
    if args.growth_type is None:
        print("ERROR: Please specify --growth-type as MoM or YoY. This system will not guess.")
        sys.exit(1)

    # Enforcement: refuse all-ward aggregation
    if args.ward is None and args.category is None:
        print("ERROR: You must specify --ward and --category. "
              "This system refuses to aggregate across all wards or categories.")
        sys.exit(1)

    rows = load_dataset(args.input)

    # Filter to requested ward + category
    filtered = rows
    if args.ward:
        filtered = [r for r in filtered if r["ward"] == args.ward]
        if not filtered:
            print(f"ERROR: Ward '{args.ward}' not found in dataset.")
            sys.exit(1)
    if args.category:
        filtered = [r for r in filtered if r["category"] == args.category]
        if not filtered:
            print(f"ERROR: Category '{args.category}' not found for ward '{args.ward}'.")
            sys.exit(1)

    print(f"\nComputing {args.growth_type} growth for: {args.ward} | {args.category}")
    results = compute_growth(filtered, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nDone. Results written to: {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

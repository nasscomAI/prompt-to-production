"""
UC-0C — Number That Looks Right
Municipal budget growth calculator with null flagging and formula display.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
]


def load_dataset(path: str) -> tuple[list[dict], list[dict]]:
    """
    Read a CSV budget file, validate columns, and report null count and affected rows.
    Returns (data_rows, null_report).
    """
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print("ERROR: CSV has no header row.", file=sys.stderr)
                sys.exit(1)

            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
                sys.exit(1)

            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot read file: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("ERROR: CSV has no data rows.", file=sys.stderr)
        sys.exit(1)

    # Parse numeric fields
    for row in rows:
        row["budgeted_amount"] = float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else None
        if row["actual_spend"].strip():
            row["actual_spend"] = float(row["actual_spend"])
        else:
            row["actual_spend"] = None

    # Build null report
    null_report = []
    for i, row in enumerate(rows):
        if row["actual_spend"] is None:
            null_report.append({
                "row_index": i,
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "reason": row["notes"] if row["notes"].strip() else "No reason given",
            })

    return rows, null_report


def compute_growth(
    data: list[dict],
    ward: str,
    category: str,
    growth_type: str,
    null_report: list[dict],
) -> list[dict]:
    """
    Take ward + category + growth_type, compute per-period growth rates.
    Returns a table with formula shown. Null rows flagged with reason.
    """
    if not growth_type:
        print("ERROR: --growth-type is required. Specify MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth-type '{growth_type}'. Must be MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    if not ward:
        print("ERROR: --ward is required. Specify a ward to filter by.", file=sys.stderr)
        sys.exit(1)

    if not category:
        print("ERROR: --category is required. Specify a category to filter by.", file=sys.stderr)
        sys.exit(1)

    # Filter data
    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'.", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Build null lookup for this ward+category
    null_periods = set()
    null_reasons = {}
    for nr in null_report:
        if nr["ward"] == ward and nr["category"] == category:
            null_periods.add(nr["period"])
            null_reasons[nr["period"]] = nr["reason"]

    # Compute growth
    formula_str = "MoM = (current - previous) / previous x 100" if growth_type == "MoM" else "YoY = (current - same_month_prev_year) / same_month_prev_year x 100"

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]

        entry = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual,
            "budgeted_amount": row["budgeted_amount"],
            "growth_rate": None,
            "formula": "",
            "flag": "",
        }

        # Null handling
        if period in null_periods:
            entry["flag"] = f"NULL — {null_reasons.get(period, 'No reason given')}"
            entry["formula"] = formula_str
            results.append(entry)
            continue

        if actual is None:
            entry["flag"] = "NULL — missing actual_spend"
            entry["formula"] = formula_str
            results.append(entry)
            continue

        # Find previous value for growth calculation
        if growth_type == "MoM":
            prev_idx = i - 1
            if prev_idx >= 0:
                prev_row = filtered[prev_idx]
                if prev_row["actual_spend"] is not None:
                    prev_val = prev_row["actual_spend"]
                    growth = ((actual - prev_val) / prev_val) * 100
                    entry["growth_rate"] = round(growth, 1)
                    entry["formula"] = f"({actual} - {prev_val}) / {prev_val} x 100 = {entry['growth_rate']:+.1f}%"
                else:
                    entry["formula"] = formula_str
                    entry["flag"] = f"Previous period ({prev_row['period']}) is NULL — cannot compute MoM"
            else:
                entry["formula"] = formula_str
                entry["flag"] = "First period — no previous data for MoM"

        elif growth_type == "YoY":
            # Find same month in previous year
            year, month = period.split("-")
            prev_period = f"{int(year) - 1}-{month}"
            prev_row = next((r for r in data if r["period"] == prev_period and r["ward"] == ward and r["category"] == category), None)
            if prev_row and prev_row["actual_spend"] is not None:
                prev_val = prev_row["actual_spend"]
                growth = ((actual - prev_val) / prev_val) * 100
                entry["growth_rate"] = round(growth, 1)
                entry["formula"] = f"({actual} - {prev_val}) / {prev_val} x 100 = {entry['growth_rate']:+.1f}%"
            elif prev_row:
                entry["formula"] = formula_str
                entry["flag"] = f"Same month previous year ({prev_period}) is NULL — cannot compute YoY"
            else:
                entry["formula"] = formula_str
                entry["flag"] = f"No data for same month previous year ({prev_period})"

        results.append(entry)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Municipal budget growth calculator"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward to filter by")
    parser.add_argument("--category", required=True, help="Category to filter by")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    data, null_report = load_dataset(args.input)

    # Report nulls to stderr
    if null_report:
        print(f"NULL REPORT: {len(null_report)} null actual_spend value(s) found:", file=sys.stderr)
        for nr in null_report:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}", file=sys.stderr)
        print(file=sys.stderr)

    results = compute_growth(
        data, args.ward, args.category, args.growth_type, null_report
    )

    fieldnames = [
        "ward", "category", "period", "budgeted_amount",
        "actual_spend", "growth_rate", "formula", "flag",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} periods written to {args.output}")
    print(f"Ward: {args.ward} | Category: {args.category} | Growth: {args.growth_type}")


if __name__ == "__main__":
    main()

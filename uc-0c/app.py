"""
UC-0C — Number That Looks Right
Ward-level budget growth calculator. Operates strictly on a single ward + single category.
Never aggregates across wards or categories. Refuses ambiguous or underspecified requests.
"""
import argparse
import csv
import os
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path):
    """
    Reads CSV, validates columns, reports nulls with reasons.
    Refuses if required columns missing or file not found.
    Returns: (list of dicts with parsed numeric fields, null_report list)
    """
    if not os.path.isfile(file_path):
        print(f"ERROR: File not found — {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            print(f"ERROR: Missing required columns: {', '.join(sorted(missing))}", file=sys.stderr)
            sys.exit(1)

        rows = []
        null_report = []
        for row in reader:
            # Parse budgeted_amount
            budget_raw = row.get("budgeted_amount", "").strip()
            try:
                row["_budgeted_amount"] = float(budget_raw) if budget_raw else None
            except ValueError:
                print(f"ERROR: Non-numeric budgeted_amount '{budget_raw}' at {row['period']} {row['ward']} {row['category']}", file=sys.stderr)
                sys.exit(1)

            # Parse actual_spend — nulls are flagged, never silently filled
            actual = row.get("actual_spend", "").strip()
            if actual == "":
                reason = row.get("notes", "").strip() or "no reason provided"
                null_report.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": reason,
                })
                row["_actual_spend"] = None
                row["_null_flag"] = reason
            else:
                try:
                    row["_actual_spend"] = float(actual)
                except ValueError:
                    print(f"ERROR: Non-numeric actual_spend '{actual}' at {row['period']} {row['ward']} {row['category']}", file=sys.stderr)
                    sys.exit(1)
                row["_null_flag"] = None
            rows.append(row)

    # Report nulls before computing — agents.md enforcement rule 2
    if null_report:
        print(f"WARNING: {len(null_report)} null actual_spend row(s) flagged:", file=sys.stderr)
        for nr in null_report:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['reason']}", file=sys.stderr)

    return rows, null_report


def compute_growth(ward, category, growth_type, dataset):
    """
    Filters by ward+category, returns per-period growth table with formulas.
    Null actual_spend rows are included with NULL and an explicit flag.
    """
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: --growth-type must be 'MoM' or 'YoY', got '{growth_type}'", file=sys.stderr)
        sys.exit(1)

    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in dataset))
        available_categories = sorted(set(r["category"] for r in dataset))
        print(f"ERROR: No data found for ward='{ward}', category='{category}'", file=sys.stderr)
        print(f"  Available wards:      {', '.join(available_wards)}", file=sys.stderr)
        print(f"  Available categories: {', '.join(available_categories)}", file=sys.stderr)
        sys.exit(1)

    filtered.sort(key=lambda r: r["period"])

    non_null = [r for r in filtered if r["_actual_spend"] is not None]
    if not non_null:
        print(f"ERROR: No non-null actual_spend values for ward='{ward}', category='{category}'. Growth cannot be computed.", file=sys.stderr)
        sys.exit(1)

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["_actual_spend"]
        null_flag = row.get("_null_flag")

        # Null row — include with NULL and flag from notes column
        if actual_spend is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula": f"flagged — null actual_spend: {null_flag}",
            })
            continue

        if growth_type == "MoM":
            prev = filtered[i - 1] if i > 0 else None
            prev_val = prev["_actual_spend"] if prev is not None else None
            if prev_val is None:
                formula = "N/A — previous period has null actual_spend"
                growth = None
            elif prev_val == 0:
                formula = "N/A — previous actual_spend is 0 (division by zero)"
                growth = None
            else:
                formula = f"({actual_spend} - {prev_val}) / {prev_val} * 100"
                growth = round((actual_spend - prev_val) / prev_val * 100, 1)
        else:  # YoY
            prev_period = f"{int(period[:4]) - 1}{period[4:]}"
            prev_row = next((r for r in dataset if r["ward"] == ward and r["category"] == category and r["period"] == prev_period), None)
            prev_val = prev_row["_actual_spend"] if prev_row is not None else None
            if prev_val is None:
                formula = f"N/A — no data or null actual_spend for {prev_period}"
                growth = None
            elif prev_val == 0:
                formula = f"N/A — {prev_period} actual_spend is 0 (division by zero)"
                growth = None
            else:
                formula = f"({actual_spend} - {prev_val}) / {prev_val} * 100"
                growth = round((actual_spend - prev_val) / prev_val * 100, 1)

        if growth is not None:
            sign = "+" if growth >= 0 else ""
            growth_str = f"{sign}{growth}%"
        else:
            growth_str = "N/A"

        results.append({
            "period": period,
            "actual_spend": str(actual_spend),
            "growth_pct": growth_str,
            "formula": formula,
        })

    return results


def write_output(results, output_path):
    """Writes the growth table to CSV with columns: period, actual_spend, growth_pct, formula."""
    fieldnames = ["period", "actual_spend", "growth_pct", "formula"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C — Ward-level budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward (exact match)")
    parser.add_argument("--category", required=True, help="Target category (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (Month-over-Month) or YoY (Year-over-Year)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    dataset, null_report = load_dataset(args.input)

    results = compute_growth(args.ward, args.category, args.growth_type, dataset)

    write_output(results, args.output)

    # Print the table to stdout — agents.md: table with period, actual_spend, growth_pct, formula
    print(f"\nWard: {args.ward} | Category: {args.category} | Growth Type: {args.growth_type}")
    print(f"{'period':<12} {'actual_spend':>14} {'growth_pct':>12}  {'formula'}")
    print("-" * 90)
    for r in results:
        print(f"{r['period']:<12} {r['actual_spend']:>14} {r['growth_pct']:>12}  {r['formula']}")

    if null_report:
        print(f"\nNull rows flagged ({len(null_report)}):")
        for nr in null_report:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['reason']}")

    print(f"\nOutput written to: {args.output}")


if __name__ == "__main__":
    main()

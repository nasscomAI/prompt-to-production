"""
UC-0C — Number That Looks Right
Computes Month-over-Month (MoM) growth for ward budget data.
Enforcement: per-ward per-category only, flags nulls, shows formula, refuses aggregation.
"""
import argparse
import csv
import sys


def load_dataset(input_path: str) -> tuple:
    """
    Read CSV, validate columns, report null count and which rows.
    Returns: (rows, null_rows) where null_rows contains details of missing data.
    """
    rows = []
    null_rows = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate columns
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames)):
            missing = required_cols - set(reader.fieldnames)
            print(f"ERROR: Missing columns: {missing}")
            sys.exit(1)

        for row in reader:
            rows.append(row)
            if not row["actual_spend"] or row["actual_spend"].strip() == "":
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row.get("notes", "No reason provided").strip()
                })

    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Null actual_spend values: {len(null_rows)}")
    if null_rows:
        print("\nNULL ROWS FLAGGED:")
        for nr in null_rows:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
        print()

    return rows, null_rows


def compute_growth(rows: list, null_rows: list, ward: str, category: str,
                   growth_type: str, output_path: str):
    """
    Compute per-period growth table for a specific ward + category.
    Shows formula used in every output row alongside the result.
    Flags null rows — does not compute growth for them.
    """
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: --growth-type must be 'MoM' or 'YoY'. Got: '{growth_type}'")
        print("Refusing to guess growth type. Please specify explicitly.")
        sys.exit(1)

    # Filter rows for the specified ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'")
        print(f"Available wards: {sorted(set(r['ward'] for r in rows))}")
        print(f"Available categories: {sorted(set(r['category'] for r in rows))}")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Identify null periods for this ward+category
    null_periods = set()
    for nr in null_rows:
        if nr["ward"] == ward and nr["category"] == category:
            null_periods.add(nr["period"])

    # Compute growth
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"].strip() if row["actual_spend"] else ""

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual else "NULL",
            "growth_pct": "",
            "formula": "",
            "flag": ""
        }

        if period in null_periods:
            result["flag"] = f"NULL — not computed. Reason: {row.get('notes', '').strip()}"
            result["formula"] = "N/A (null value)"
            results.append(result)
            continue

        if i == 0:
            result["formula"] = "N/A (first period — no prior value)"
            result["flag"] = "Baseline period"
            results.append(result)
            continue

        # Check if previous period is null
        prev_row = filtered[i - 1]
        prev_period = prev_row["period"]
        prev_actual = prev_row["actual_spend"].strip() if prev_row["actual_spend"] else ""

        if prev_period in null_periods or not prev_actual:
            result["formula"] = f"N/A (prior period {prev_period} is NULL)"
            result["flag"] = "Cannot compute — prior period null"
            results.append(result)
            continue

        # Compute MoM growth
        try:
            current_val = float(actual)
            prev_val = float(prev_actual)

            if prev_val == 0:
                result["formula"] = f"({current_val} - 0) / 0 = undefined"
                result["flag"] = "Division by zero — prior period was 0"
            else:
                growth = ((current_val - prev_val) / prev_val) * 100
                result["growth_pct"] = f"{growth:+.1f}%"
                result["formula"] = f"({current_val} - {prev_val}) / {prev_val} * 100 = {growth:+.1f}%"
        except ValueError as e:
            result["flag"] = f"Error parsing values: {e}"
            result["formula"] = "N/A (parse error)"

        results.append(result)

    # Write output
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nGrowth output written to: {output_path}")
    print(f"Ward: {ward}")
    print(f"Category: {category}")
    print(f"Growth type: {growth_type}")
    print(f"Periods computed: {len(results)}")
    null_count = sum(1 for r in results if "NULL" in r.get("flag", ""))
    if null_count:
        print(f"Null periods flagged (not computed): {null_count}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (Month-over-Month) or YoY (Year-over-Year)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    compute_growth(rows, null_rows, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()

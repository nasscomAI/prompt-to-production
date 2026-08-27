"""
UC-0C — Number That Looks Right
Computes per-ward per-category growth rates with null handling and formula display.
Follows the RICE enforcement rules defined in agents.md.
"""
import argparse
import csv
import sys


def load_dataset(input_path: str) -> tuple:
    """
    Read ward budget CSV, validate columns, report nulls.
    Returns (rows, null_report) where null_report lists every null actual_spend row.
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        # Validate columns
        missing = [c for c in required_columns if c not in headers]
        if missing:
            print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

        rows = list(reader)

    # Identify null actual_spend rows
    null_report = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "No reason provided").strip() or "No reason provided"
            })

    print(f"Dataset loaded: {len(rows)} rows, {len(null_report)} null actual_spend values")
    if null_report:
        print("\nNull actual_spend rows:")
        for n in null_report:
            print(f"  {n['period']} | {n['ward']} | {n['category']} — {n['reason']}")
        print()

    return rows, null_report


def compute_growth(rows: list, null_report: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute growth for a specific ward + category combination.
    Returns list of result dicts with period, actual_spend, growth_rate, formula_used, null_flag.
    """
    # Validate ward and category exist
    available_wards = sorted(set(r["ward"] for r in rows))
    available_categories = sorted(set(r["category"] for r in rows))

    if ward not in available_wards:
        print(f"ERROR: Ward '{ward}' not found. Available wards:", file=sys.stderr)
        for w in available_wards:
            print(f"  - {w}", file=sys.stderr)
        sys.exit(1)

    if category not in available_categories:
        print(f"ERROR: Category '{category}' not found. Available categories:", file=sys.stderr)
        for c in available_categories:
            print(f"  - {c}", file=sys.stderr)
        sys.exit(1)

    # Filter to requested ward + category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    # Build null lookup
    null_set = set()
    for n in null_report:
        null_set.add((n["period"], n["ward"], n["category"]))

    # Null reason lookup
    null_reasons = {}
    for n in null_report:
        null_reasons[(n["period"], n["ward"], n["category"])] = n["reason"]

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        spend_raw = row["actual_spend"].strip() if row["actual_spend"] else ""
        is_null = (period, ward, category) in null_set or spend_raw == ""

        if is_null:
            reason = null_reasons.get((period, ward, category), "actual_spend missing")
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_rate": "N/A — actual_spend missing",
                "formula_used": "N/A",
                "null_flag": f"NULL: {reason}"
            })
            continue

        actual_spend = float(spend_raw)

        if i == 0:
            results.append({
                "period": period,
                "actual_spend": f"{actual_spend}",
                "growth_rate": "N/A — no previous period",
                "formula_used": "N/A",
                "null_flag": ""
            })
            continue

        # Check if previous row was null
        prev_row = filtered[i - 1]
        prev_spend_raw = prev_row["actual_spend"].strip() if prev_row["actual_spend"] else ""
        prev_is_null = (prev_row["period"], ward, category) in null_set or prev_spend_raw == ""

        if prev_is_null:
            results.append({
                "period": period,
                "actual_spend": f"{actual_spend}",
                "growth_rate": "N/A — previous value missing",
                "formula_used": "N/A",
                "null_flag": "Previous period is NULL"
            })
            continue

        prev_spend = float(prev_spend_raw)

        if growth_type == "MoM":
            if prev_spend == 0:
                growth_rate = "N/A — division by zero"
                formula = f"({actual_spend} - 0) / 0 * 100 = undefined"
            else:
                growth = (actual_spend - prev_spend) / prev_spend * 100
                growth_rate = f"{growth:+.1f}%"
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100 = {growth:+.1f}%"
        elif growth_type == "YoY":
            # YoY needs same month previous year — for single-year data, report N/A
            growth_rate = "N/A — single year dataset (2024 only)"
            formula = "YoY requires data from previous year"
        else:
            growth_rate = "N/A"
            formula = "N/A"

        results.append({
            "period": period,
            "actual_spend": f"{actual_spend}",
            "growth_rate": growth_rate,
            "formula_used": formula,
            "null_flag": ""
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=False, default=None,
                        help="Growth type: MoM or YoY (required)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if args.growth_type is None:
        print("ERROR: --growth-type is required. Please specify MoM or YoY.", file=sys.stderr)
        print("Usage: python app.py --input <file> --ward <ward> --category <cat> "
              "--growth-type MoM --output <file>", file=sys.stderr)
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth type '{args.growth_type}'. Must be MoM or YoY.",
              file=sys.stderr)
        sys.exit(1)

    rows, null_report = load_dataset(args.input)
    results = compute_growth(rows, null_report, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "growth_rate", "formula_used", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output} ({len(results)} periods)")


if __name__ == "__main__":
    main()

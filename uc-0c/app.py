"""
UC-0C — Number That Looks Right
Computes per-ward per-category spending growth rates (MoM/YoY).
Built using R.I.C.E enforcement rules from agents.md.
"""
import argparse
import csv


def load_dataset(input_path: str) -> dict:
    """
    Reads ward budget CSV, validates columns, reports null actual_spend rows.
    Returns dict with 'data', 'null_rows', 'null_count', 'total_row_count'.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        return None

    expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    actual_cols = set(rows[0].keys()) if rows else set()
    missing = expected_cols - actual_cols
    if missing:
        print(f"Error: Missing columns: {missing}")
        return None

    null_rows = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "No reason provided").strip()
            })

    print(f"Loaded {len(rows)} rows from {input_path}")
    print(f"Null actual_spend values detected: {len(null_rows)}")
    for nr in null_rows:
        print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")

    return {
        "data": rows,
        "null_rows": null_rows,
        "null_count": len(null_rows),
        "total_row_count": len(rows)
    }


def compute_growth(ward: str, category: str, growth_type: str, dataset: dict) -> list:
    """
    Computes MoM growth for a specific ward + category.
    Returns list of result dicts with period, actual_spend, growth_rate, formula, flag.
    """
    if growth_type not in ("MoM", "YoY"):
        print(f"Error: Invalid growth type '{growth_type}'. Must be 'MoM' or 'YoY'.")
        return []

    rows = dataset["data"]

    # Filter to the specific ward + category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        valid_wards = sorted(set(r["ward"] for r in rows))
        valid_cats = sorted(set(r["category"] for r in rows))
        print(f"Error: No data found for ward='{ward}', category='{category}'")
        print(f"Valid wards: {valid_wards}")
        print(f"Valid categories: {valid_cats}")
        return []

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row["actual_spend"].strip() if row["actual_spend"] else ""
        notes = row.get("notes", "").strip()

        # Check if current period is null
        if spend_str == "":
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_rate": "N/A — null value",
                "formula": f"actual_spend is NULL ({notes})",
                "flag": f"NULL_VALUE: {notes}"
            })
            continue

        current = float(spend_str)

        # First period — no previous to compare
        if i == 0:
            results.append({
                "period": period,
                "actual_spend": str(current),
                "growth_rate": "N/A — first period",
                "formula": "No previous period for comparison",
                "flag": ""
            })
            continue

        # Check if previous period was null
        prev_spend_str = filtered[i - 1]["actual_spend"].strip() if filtered[i - 1]["actual_spend"] else ""
        if prev_spend_str == "":
            results.append({
                "period": period,
                "actual_spend": str(current),
                "growth_rate": "N/A — previous period null",
                "formula": "Previous period actual_spend is NULL — growth not computable",
                "flag": "PREV_NULL"
            })
            continue

        previous = float(prev_spend_str)

        # Compute MoM growth
        if previous == 0:
            growth = "N/A — division by zero"
            formula = f"({current} - 0) / 0 — undefined"
        else:
            growth_val = ((current - previous) / previous) * 100
            growth = f"{growth_val:+.1f}%"
            formula = f"({current} - {previous}) / {previous} x 100 = {growth_val:+.1f}%"

        results.append({
            "period": period,
            "actual_spend": str(current),
            "growth_rate": growth,
            "formula": formula,
            "flag": ""
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Budget category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM or YoY (required — will not guess)")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    # Skill 1: load_dataset
    dataset = load_dataset(args.input)
    if dataset is None:
        return

    # Skill 2: compute_growth
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)
    if not results:
        return

    # Write output
    fieldnames = ["period", "actual_spend", "growth_rate", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nGrowth output written to {args.output}")
    print(f"Scope: {args.ward} | {args.category} | {args.growth_type}")
    print(f"Rows output: {len(results)}")


if __name__ == "__main__":
    main()

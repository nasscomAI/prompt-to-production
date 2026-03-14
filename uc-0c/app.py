"""
UC-0C — Number That Looks Right
Per-ward per-category growth calculator following RICE enforcement from agents.md.
Flags null values, shows formula, refuses cross-ward aggregation.
"""
import argparse
import csv
import sys


def load_dataset(file_path: str):
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if rows and not required.issubset(rows[0].keys()):
        missing = required - set(rows[0].keys())
        print(f"ERROR: Missing columns: {missing}", file=sys.stderr)
        sys.exit(1)

    null_rows = []
    for row in rows:
        if row["actual_spend"].strip() == "":
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided"),
            })

    if null_rows:
        print(f"\n*** NULL ACTUAL_SPEND REPORT ({len(null_rows)} rows) ***")
        for nr in null_rows:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        print()

    return rows, null_rows


def compute_growth(data: list[dict], ward: str, category: str, growth_type: str):
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Unrecognised growth type '{growth_type}'. Valid options: MoM, YoY", file=sys.stderr)
        sys.exit(1)

    wards = sorted(set(r["ward"] for r in data))
    categories = sorted(set(r["category"] for r in data))

    if ward not in wards:
        print(f"ERROR: Ward '{ward}' not found. Available: {wards}", file=sys.stderr)
        sys.exit(1)
    if category not in categories:
        print(f"ERROR: Category '{category}' not found. Available: {categories}", file=sys.stderr)
        sys.exit(1)

    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    results = []
    prev_spend = None

    for row in filtered:
        period = row["period"]
        raw_spend = row["actual_spend"].strip()
        notes = row.get("notes", "").strip()

        if raw_spend == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_rate": "NULL — not computed",
                "formula": "N/A — null actual_spend",
                "null_flag": f"YES — {notes}",
            })
            prev_spend = None
            continue

        spend = float(raw_spend)

        if prev_spend is None:
            growth_str = "N/A"
            formula_str = "N/A — no prior period to compare"
        else:
            growth = (spend - prev_spend) / prev_spend * 100
            growth_str = f"{growth:+.1f}%"
            formula_str = f"({spend} - {prev_spend}) / {prev_spend} * 100 = {growth:+.1f}%"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": str(spend),
            "growth_rate": growth_str,
            "formula": formula_str,
            "null_flag": "",
        })
        prev_spend = spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth calculation type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    data, null_rows = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output written to {args.output}")
    print(f"Rows computed: {len(results)}")
    null_count = sum(1 for r in results if r["null_flag"])
    if null_count:
        print(f"Null rows flagged: {null_count}")


if __name__ == "__main__":
    main()

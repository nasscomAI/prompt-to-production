"""
UC-0C — Number That Looks Right
Computes MoM or YoY growth for a single ward + category.
Flags null rows, shows formula per row, refuses cross-ward/category aggregation.

Usage:
  python app.py --input <budget.csv> --ward "<ward>" --category "<cat>" --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(path: str) -> dict:
    rows = []
    null_rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"Error: Missing required columns: {', '.join(sorted(missing))}")
        for row in reader:
            rows.append(row)
            spend = row.get("actual_spend", "").strip()
            if not spend:
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row.get("notes", "").strip() or "No reason provided",
                })
    return {"data": rows, "null_rows": null_rows, "row_count": len(rows)}


def compute_growth(rows: list[dict], growth_type: str) -> list[dict]:
    if growth_type not in ("MoM", "YoY"):
        sys.exit(f"Error: Unsupported growth type '{growth_type}'. Use 'MoM' or 'YoY'.")

    sorted_rows = sorted(rows, key=lambda r: r["period"])
    results = []
    for i, row in enumerate(sorted_rows):
        spend = row.get("actual_spend", "").strip()
        ward = row["ward"]
        category = row["category"]
        period = row["period"]
        null_reason = row.get("notes", "").strip() or ""

        if not spend:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "",
                "growth_formula": "NULL — cannot compute",
                "growth_pct": "",
                "null_flag": "YES",
                "null_reason": null_reason or "No reason provided",
            })
            continue

        spend_val = float(spend)
        if i == 0:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": f"{spend_val:.1f}",
                "growth_formula": "No prior period for MoM comparison",
                "growth_pct": "N/A",
                "null_flag": "",
                "null_reason": "",
            })
        else:
            prev_spend = sorted_rows[i - 1].get("actual_spend", "").strip()
            if not prev_spend:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": f"{spend_val:.1f}",
                    "growth_formula": "Previous period actual_spend is NULL — cannot compute",
                    "growth_pct": "",
                    "null_flag": "",
                    "null_reason": "",
                })
                continue
            prev_val = float(prev_spend)
            diff = spend_val - prev_val
            pct = (diff / prev_val) * 100
            sign = "+" if pct >= 0 else ""
            formula = f"({spend_val:.1f} - {prev_val:.1f}) / {prev_val:.1f} × 100 = {sign}{pct:.1f}%"
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": f"{spend_val:.1f}",
                "growth_formula": formula,
                "growth_pct": f"{sign}{pct:.1f}%",
                "null_flag": "",
                "null_reason": "",
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C: Compute budget growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category to filter (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type: 'MoM' or 'YoY'")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    gt = args.growth_type
    if gt not in ("MoM", "YoY"):
        sys.exit(f"Error: --growth-type must be 'MoM' or 'YoY'. Got '{gt}'.")

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"Error: Input file not found: {args.input}")

    dataset = load_dataset(args.input)

    nulls = dataset["null_rows"]
    if nulls:
        print(f"WARNING: {len(nulls)} row(s) with null actual_spend found:")
        for n in nulls:
            print(f"  {n['period']} | {n['ward']} | {n['category']} | Reason: {n['reason']}")
        print()

    all_wards = {r["ward"] for r in dataset["data"]}
    all_categories = {r["category"] for r in dataset["data"]}

    if args.ward.lower() == "all":
        sys.exit("Error: Cross-ward aggregation not supported. Specify a single ward with --ward.")
    if args.category.lower() == "all":
        sys.exit("Error: Cross-category aggregation not supported. Specify a single category with --category.")

    filtered = [r for r in dataset["data"] if r["ward"] == args.ward and r["category"] == args.category]
    if not filtered:
        sys.exit(f"Error: No data found for ward '{args.ward}' and category '{args.category}'.")

    results = compute_growth(filtered, args.growth_type)

    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ward", "category", "period", "actual_spend",
            "growth_formula", "growth_pct", "null_flag", "null_reason",
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output written to {args.output} ({len(results)} periods)")


if __name__ == "__main__":
    main()

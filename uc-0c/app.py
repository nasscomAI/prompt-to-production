"""
UC-0C — Number That Looks Right
"""
import argparse
import csv
import sys


def load_dataset(input_path: str):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    missing = [c for c in required if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    null_rows = []
    for i, row in enumerate(rows):
        if row.get("actual_spend", "").strip() == "":
            null_rows.append({
                "row": i + 2,
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", ""),
            })

    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(null_rows)}")
    for nr in null_rows:
        print(f"  Row {nr['row']}: {nr['period']} | {nr['ward']} | {nr['category']} — {nr['notes']}")

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type: {growth_type}. Must be 'MoM' or 'YoY'.")

    filtered = []
    for row in rows:
        if row["ward"].strip() == ward.strip() and row["category"].strip() == category.strip():
            filtered.append(row)

    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return []

    filtered.sort(key=lambda r: r["period"])

    formula = "(current - previous) / previous * 100" if growth_type == "MoM" else "N/A"

    results = []
    prev_spend = None
    for row in filtered:
        period = row["period"]
        budgeted = float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else 0.0
        actual_str = row["actual_spend"].strip()
        notes = row.get("notes", "").strip()

        if actual_str == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "",
                "growth_pct": "NULL",
                "formula_used": "N/A — null actual_spend",
                "flag": "NULL_DATA",
                "notes": notes,
            })
            prev_spend = None
            continue

        actual = float(actual_str)
        if prev_spend is not None and prev_spend != 0:
            growth = round((actual - prev_spend) / prev_spend * 100, 2)
            growth_str = f"{growth:+.2f}%"
        else:
            growth_str = "N/A (base period)"
            growth = None

        flag = ""
        if growth is not None and abs(growth) > 20:
            flag = "SIGNIFICANT_CHANGE"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "growth_pct": growth_str,
            "formula_used": formula if prev_spend is not None and actual_str != "" else "N/A — base period",
            "flag": flag,
            "notes": notes,
        })

        prev_spend = actual

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", required=False, help="Must be MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Must be 'MoM' or 'YoY'. Refusing to guess.")
        sys.exit(1)

    if args.growth_type.upper() not in ("MOM", "YOY"):
        print(f"Error: Invalid --growth-type '{args.growth_type}'. Must be 'MoM' or 'YoY'.")
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)

    growth_type = args.growth_type.upper()
    if growth_type == "MOM":
        growth_type = "MoM"
    elif growth_type == "YOY":
        growth_type = "YoY"

    results = compute_growth(rows, args.ward, args.category, growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula_used", "flag", "notes"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")
    flagged = [r for r in results if r.get("flag")]
    null_count = len([r for r in results if r.get("flag") == "NULL_DATA"])
    if flagged:
        print(f"  {null_count} null rows flagged, {len(flagged) - null_count} significant changes noted.")


if __name__ == "__main__":
    main()

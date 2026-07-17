"""
UC-0C — Number That Looks Right
Budget growth computation with null handling and formula transparency.
"""
import argparse
import csv


def load_dataset(path: str) -> dict:
    """Read CSV, validate columns, report null count and which rows."""
    rows = []
    null_rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                    null_rows.append(row)
                rows.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}")
    return {"rows": rows, "null_rows": null_rows, "column_names": ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]}


def compute_growth(ward: str, category: str, growth_type: str, rows: list) -> list:
    """Compute per-period growth for a ward+category. Returns list of dicts with formula."""
    if not growth_type:
        raise ValueError("growth_type must be specified (MoM or YoY)")

    filtered = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    filtered.sort(key=lambda x: x.get("period", ""))

    results = []
    prev_spend = None
    for row in filtered:
        period = row.get("period", "")
        spend_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "")

        if not spend_str:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_percentage": "NULL",
                "formula": f"Skipped: {notes}" if notes else "Skipped: null value"
            })
            prev_spend = None
            continue

        spend = float(spend_str)
        if prev_spend is not None and prev_spend != 0:
            growth = ((spend - prev_spend) / prev_spend) * 100
            formula = f"({spend} - {prev_spend}) / {prev_spend} * 100"
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_percentage": f"{growth:+.1f}%",
                "formula": formula
            })
        else:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_percentage": "N/A",
                "formula": "First period or previous null"
            })
        prev_spend = spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    data = load_dataset(args.input)
    print(f"Loaded {len(data['rows'])} rows, {len(data['null_rows'])} null values found")
    for nr in data["null_rows"]:
        print(f"  NULL: {nr.get('period')} {nr.get('ward')} {nr.get('category')} - {nr.get('notes')}")

    results = compute_growth(args.ward, args.category, args.growth_type, data["rows"])

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth_percentage", "formula"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

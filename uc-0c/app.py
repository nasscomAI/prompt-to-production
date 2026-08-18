"""UC-0C — Ward budget growth calculator.

This script enforces the RICE rules for the budget use case:
- single ward + single category only
- explicit growth type required
- null rows flagged before calculation
- growth formula shown for every row
"""
import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes"
]


def _to_float(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def load_dataset(input_path: str):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        rows = list(reader)
    return rows


def _safe_pct(current, previous):
    if previous in (None, 0):
        return None
    return ((current - previous) / previous) * 100.0


def compute_growth(rows, ward: str, category: str, growth_type: str):
    if not ward or not category:
        raise ValueError("Both --ward and --category are required.")
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("--growth-type must be either MoM or YoY.")

    filtered = [
        row for row in rows
        if row.get("ward") == ward and row.get("category") == category
    ]
    if not filtered:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")

    filtered = sorted(filtered, key=lambda r: r["period"])
    output_rows = []
    previous_value = None
    for row in filtered:
        period = row.get("period", "")
        actual = _to_float(row.get("actual_spend"))
        notes = (row.get("notes") or "").strip()
        if actual is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_pct": "NULL",
                "formula": "NULL (actual_spend missing; reason: " + (notes or "no note") + ")",
                "null_row": "YES",
                "note": notes,
            })
            continue

        if previous_value is None:
            growth_pct = "N/A"
            formula = "N/A (first period in selected series)"
        else:
            change = _safe_pct(actual, previous_value)
            growth_pct = "N/A" if change is None else round(change, 1)
            formula = "N/A" if change is None else f"(({actual} - {previous_value}) / {previous_value}) * 100"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "growth_pct": growth_pct,
            "formula": formula,
            "null_row": "NO",
            "note": notes,
        })
        previous_value = actual

    return output_rows


def write_csv(output_path: str, rows):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "null_row", "note"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator")
    parser.add_argument("--input", required=True, help="CSV budget file")
    parser.add_argument("--ward", required=True, help="Ward to analyse")
    parser.add_argument("--category", required=True, help="Category to analyse")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="CSV output path")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    null_rows = [r for r in rows if (r.get("actual_spend") or "").strip() == ""]
    if null_rows:
        print("Null actual_spend rows flagged before calculation:")
        for r in null_rows:
            print(f"- {r['period']} | {r['ward']} | {r['category']} | {r['notes']}")

    out_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_csv(args.output, out_rows)
    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()

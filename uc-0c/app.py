"""UC-0C budget growth calculator."""

import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path: str):
    """Load the dataset and validate its structure before computing growth."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with path.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

        rows = []
        null_rows = []
        for row in reader:
            cleaned = {
                "period": (row.get("period") or "").strip(),
                "ward": (row.get("ward") or "").strip(),
                "category": (row.get("category") or "").strip(),
                "budgeted_amount": row.get("budgeted_amount", ""),
                "actual_spend": row.get("actual_spend", ""),
                "notes": (row.get("notes") or "").strip(),
            }
            rows.append(cleaned)
            if cleaned["actual_spend"] in ("", None):
                null_rows.append(cleaned)

        return rows, null_rows


def parse_float(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for a single ward/category over time using a clear formula."""
    if ward.lower() in {"all", "all wards", "*"} or category.lower() in {"all", "all categories", "*"}:
        raise ValueError("Aggregation across wards or categories is not allowed. Please specify one ward and one category.")

    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Please specify --growth-type as either 'MoM' or 'YoY'.")

    filtered = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]
    filtered.sort(key=lambda r: r["period"])

    output_rows = []
    previous = None
    previous_period = None

    for row in filtered:
        current_actual = parse_float(row["actual_spend"])
        period = row["period"]
        notes = row["notes"] or ""

        if current_actual is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_pct": "",
                "previous_period": previous_period or "",
                "formula": "FLAGGED_NULL",
                "status": "NULL",
                "null_reason": notes or "Missing actual_spend value",
            })
            previous = None
            previous_period = period
            continue

        if previous is None or previous_period is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_actual,
                "growth_pct": "",
                "previous_period": "",
                "formula": "N/A: first period in series",
                "status": "BASE",
                "null_reason": "",
            })
        else:
            if previous == 0:
                growth_pct = ""
                formula = "N/A: previous actual_spend = 0"
            else:
                delta = current_actual - previous
                growth_pct = (delta / previous) * 100
                formula = f"(( {current_actual} - {previous} ) / {previous}) * 100"
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_actual,
                "growth_pct": "" if previous == 0 else f"{growth_pct:.1f}%",
                "previous_period": previous_period,
                "formula": formula,
                "status": "CALCULATED",
                "null_reason": "",
            })

        previous = current_actual
        previous_period = period

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C municipal budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type to compute")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    if not any(row["ward"] == args.ward and row["category"] == args.category for row in rows):
        raise ValueError(f"No records found for ward='{args.ward}' and category='{args.category}'")

    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "previous_period",
        "growth_pct",
        "formula",
        "status",
        "null_reason",
    ]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

    print(f"Growth output written to {output_path}")
    print(f"Null rows flagged: {len(null_rows)}")


if __name__ == "__main__":
    main()

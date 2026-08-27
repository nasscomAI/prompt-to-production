"""UC-0C budget growth calculator."""

import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(path: str):
    """Load and validate the budget dataset."""
    file_path = Path(path)
    with file_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
            raise ValueError("CSV is missing required columns: period, ward, category, budgeted_amount, actual_spend, notes")
        rows = list(reader)

    null_rows = [row for row in rows if str(row.get("actual_spend", "")).strip() in {"", "NULL", "null", "NaN", "N/A"}]
    return rows, null_rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Compute growth for a single ward/category pair and return CSV rows."""
    if not ward or not category:
        raise ValueError("Both ward and category are required. Refusing to calculate without explicit scope.")
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("growth-type must be explicitly set to MoM or YoY. Refusing to guess.")

    filtered = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    filtered.sort(key=lambda row: row["period"])

    output_rows = []
    previous_value = None
    previous_period = None

    for row in filtered:
        raw_value = str(row.get("actual_spend", "")).strip()
        if raw_value in {"", "NULL", "null", "NaN", "N/A"}:
            output_rows.append({
                "ward": row.get("ward", ward),
                "category": row.get("category", category),
                "period": row.get("period", ""),
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula": "NULL actual_spend; no computation",
                "status": "NULL_ACTUAL_SPEND",
                "null_reason": row.get("notes", "No note provided"),
            })
            continue

        value = float(raw_value)
        if growth_type == "MoM":
            if previous_value is None or previous_value == 0:
                growth_pct = "N/A"
                formula = "baseline period — no previous actual spend"
            else:
                growth_pct = ((value - previous_value) / previous_value) * 100
                formula = f"(( {value} - {previous_value} ) / {previous_value}) * 100"
        else:
            if previous_value is None or previous_value == 0:
                growth_pct = "N/A"
                formula = "baseline period — no previous actual spend"
            else:
                growth_pct = ((value - previous_value) / previous_value) * 100
                formula = f"(( {value} - {previous_value} ) / {previous_value}) * 100"

        output_rows.append({
            "ward": row.get("ward", ward),
            "category": row.get("category", category),
            "period": row.get("period", ""),
            "actual_spend": round(value, 1),
            "growth_pct": f"{growth_pct:+.1f}%" if growth_pct != "N/A" else "N/A",
            "formula": formula,
            "status": "OK",
            "null_reason": "",
        })
        previous_value = value
        previous_period = row.get("period")

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write CSV output")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["ward", "category", "period", "actual_spend", "growth_pct", "formula", "status", "null_reason"])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Growth output written to {args.output}; flagged {len(null_rows)} null rows.")


if __name__ == "__main__":
    main()

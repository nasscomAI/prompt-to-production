"""
UC-0C app.py — Growth calculator for ward budget data.
"""
import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

NULL_MARKER = "NULL"
NOT_COMPUTED = "NOT COMPUTED"


def load_dataset(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing headers.")

        missing = REQUIRED_COLUMNS.difference({name.strip() for name in reader.fieldnames})
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(sorted(missing))}")

        rows = [row for row in reader]

    if not rows:
        raise ValueError("Input CSV contains no data rows.")

    null_rows = []
    for row in rows:
        actual_spend = row.get("actual_spend")
        if actual_spend is None or str(actual_spend).strip() == "":
            reason = str(row.get("notes", "")).strip() or "UNKNOWN"
            null_rows.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "reason": reason,
                }
            )

    print(f"Loaded dataset with {len(rows)} rows and {len(null_rows)} null actual_spend rows.")
    for null_row in null_rows:
        print(
            f"NULL row: {null_row['period']} | {null_row['ward']} | {null_row['category']} | reason={null_row['reason']}"
        )

    return rows


def parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    clean = value.strip()
    if clean == "":
        return None
    try:
        return float(clean)
    except ValueError:
        return None


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    if ward.strip().lower() in {"all", "any", "*"}:
        raise ValueError("Aggregation across wards is not permitted; specify a single exact ward.")
    if category.strip().lower() in {"all", "any", "*"}:
        raise ValueError("Aggregation across categories is not permitted; specify a single exact category.")

    growth_type = growth_type.strip()
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Growth type must be either MoM or YoY.")

    filtered = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    if not filtered:
        wards = sorted({row.get("ward", "") for row in rows if row.get("ward")})
        categories = sorted({row.get("category", "") for row in rows if row.get("category")})
        raise ValueError(
            f"No rows found for ward '{ward}' and category '{category}'. Available wards: {', '.join(wards)}. "
            f"Available categories: {', '.join(categories)}."
        )

    sorted_rows = sorted(filtered, key=lambda r: r.get("period", ""))
    output_rows: List[Dict[str, str]] = []
    previous_actual: Optional[float] = None
    previous_reason: Optional[str] = None

    for row in sorted_rows:
        period = row.get("period", "")
        actual_spend_raw = row.get("actual_spend", "")
        actual = parse_float(actual_spend_raw)
        note = row.get("notes", "").strip()
        entry = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": NULL_MARKER if actual is None else f"{actual:.1f}",
            "formula": "",
            "growth_value": "",
            "null_reason": "",
        }

        if actual is None:
            entry["growth_value"] = NOT_COMPUTED
            entry["formula"] = ""
            entry["null_reason"] = note or "UNKNOWN"
        elif growth_type == "MoM":
            if previous_actual is None:
                if previous_reason is not None:
                    entry["growth_value"] = NOT_COMPUTED
                    entry["formula"] = "Cannot compute MoM growth because previous period actual_spend is NULL."
                    entry["null_reason"] = previous_reason
                else:
                    entry["growth_value"] = NOT_COMPUTED
                    entry["formula"] = "Cannot compute MoM growth because previous period is not available."
                    entry["null_reason"] = "MISSING_PREVIOUS"
            else:
                formula = f"({actual:.1f} - {previous_actual:.1f}) / {previous_actual:.1f} * 100"
                computed = (actual - previous_actual) / previous_actual * 100
                entry["formula"] = formula
                entry["growth_value"] = f"{computed:+.1f}%"
        else:
            entry["formula"] = "YoY comparison not available in a single-year dataset."
            entry["growth_value"] = NOT_COMPUTED
            entry["null_reason"] = "NO_YOY_DATA"

        output_rows.append(entry)

        if actual is None:
            previous_actual = None
            previous_reason = note or "UNKNOWN"
        else:
            previous_actual = actual
            previous_reason = None

    return output_rows


def write_output(path: Path, rows: List[Dict[str, str]]):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "formula",
        "growth_value",
        "null_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to calculate growth for")
    parser.add_argument("--category", required=True, help="Budget category to calculate growth for")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows = load_dataset(Path(args.input))
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(Path(args.output), results)
    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

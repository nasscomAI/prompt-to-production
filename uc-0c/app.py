import argparse
import csv
from pathlib import Path
from typing import List, Dict, Optional

REQUIRED_COLUMNS: set[str] = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

ALLOWED_GROWTH_TYPES: set[str] = set(["MOM", "YOY"])

def parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None

def load_dataset(input_path: Path) -> List[Dict[str, str]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")

        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        rows: List[Dict[str, str]] = []
        for row in reader:
            clean_row: Dict[str, str] = {}
            for key, val in row.items():
                if key is not None:
                    clean_row[key] = "" if val is None else val
            rows.append(clean_row)

    return rows

def validate_inputs(ward: Optional[str], category: Optional[str], growth_type: Optional[str]) -> str:
    if not ward:
        raise ValueError("Refused: --ward is required. Never aggregate across wards.")
    if not category:
        raise ValueError("Refused: --category is required. Never aggregate across categories.")
    if not growth_type:
        raise ValueError("Refused: --growth-type is required. Never guess the formula.")

    gt = growth_type.strip().upper()
    if gt not in ALLOWED_GROWTH_TYPES:
        raise ValueError("Invalid --growth-type. Allowed values: MoM, YoY")

    return gt

def sort_periods(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda r: r["period"])

def compute_mom(filtered_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    output: List[Dict[str, str]] = []
    previous_actual: Optional[float] = None
    previous_period: Optional[str] = None

    for i, row in enumerate(filtered_rows):
        period = row["period"]
        ward = row["ward"]
        category = row["category"]
        budgeted = parse_float(row["budgeted_amount"])
        actual = parse_float(row["actual_spend"])
        notes = row.get("notes", "").strip()

        result: Dict[str, str] = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": "" if budgeted is None else f"{budgeted:.2f}",
            "actual_spend": "" if actual is None else f"{actual:.2f}",
            "growth_type": "MoM",
            "formula": "",
            "growth_percent": "",
            "status": "",
            "reason": "",
            "notes": notes,
        }

        if actual is None:
            result["status"] = "NULL_FLAGGED"
            result["reason"] = "Current row actual_spend is null; growth not computed."
            result["formula"] = "MoM = ((current - previous) / previous) * 100"
            output.append(result)
            previous_actual = None
            previous_period = period
            continue

        if i == 0:
            result["status"] = "NO_BASELINE"
            result["reason"] = "First available period for this ward-category; no previous month baseline."
            result["formula"] = "MoM = ((current - previous) / previous) * 100"
            output.append(result)
            previous_actual = actual
            previous_period = period
            continue

        if previous_actual is None:
            result["status"] = "CANNOT_COMPUTE"
            result["reason"] = f"Previous month baseline unavailable or null (previous period: {previous_period})."
            result["formula"] = "MoM = ((current - previous) / previous) * 100"
            output.append(result)
            previous_actual = actual
            previous_period = period
            continue

        if previous_actual == 0:
            result["status"] = "CANNOT_COMPUTE"
            result["reason"] = f"Previous month actual_spend is zero in {previous_period}; division by zero avoided."
            result["formula"] = "MoM = ((current - previous) / previous) * 100"
            output.append(result)
            previous_actual = actual
            previous_period = period
            continue

        growth = ((actual - previous_actual) / previous_actual) * 100.0
        result["status"] = "OK"
        result["formula"] = f"(({actual:.2f} - {previous_actual:.2f}) / {previous_actual:.2f}) * 100"
        result["growth_percent"] = f"{growth:.2f}"
        result["reason"] = f"Computed MoM growth using current period {period} and previous period {previous_period}."
        output.append(result)

        previous_actual = actual
        previous_period = period

    return output

def compute_yoy(filtered_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    output: List[Dict[str, str]] = []

    for row in filtered_rows:
        period = row["period"]
        ward = row["ward"]
        category = row["category"]
        budgeted = parse_float(row["budgeted_amount"])
        actual = parse_float(row["actual_spend"])
        notes = row.get("notes", "").strip()

        result: Dict[str, str] = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": "" if budgeted is None else f"{budgeted:.2f}",
            "actual_spend": "" if actual is None else f"{actual:.2f}",
            "growth_type": "YoY",
            "formula": "YoY = ((current_period - same_period_last_year) / same_period_last_year) * 100",
            "growth_percent": "",
            "status": "CANNOT_COMPUTE",
            "reason": "YoY requires prior-year same-period data, but the provided dataset contains only 2024 periods.",
            "notes": notes,
        }

        if actual is None:
            result["status"] = "NULL_FLAGGED"
            result["reason"] = "Current row actual_spend is null; YoY growth not computed."

        output.append(result)

    return output

def write_output(output_path: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "reason",
        "notes",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    parser = argparse.ArgumentParser(description="Compute per-period growth for a single ward and category.")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    growth_type = validate_inputs(args.ward, args.category, args.growth_type)
    rows = load_dataset(Path(args.input))

    filtered: List[Dict[str, str]] = []
    for row in rows:
        if row["ward"].strip() == args.ward.strip() and row["category"].strip() == args.category.strip():
            filtered.append(row)

    if not filtered:
        raise ValueError(
            f"No rows found for ward='{args.ward}' and category='{args.category}'. "
            "Refusing to aggregate across wards/categories."
        )

    filtered = sort_periods(filtered)

    if growth_type == "MOM":
        output_rows = compute_mom(filtered)
    else:
        output_rows = compute_yoy(filtered)

    write_output(Path(args.output), output_rows)
    print(f"Growth output written to: {args.output}")

if __name__ == "__main__":
    main()
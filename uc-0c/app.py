"""
UC-0C app.py — Minimal implementation.
Loads ward budget CSV, validates the requested ward/category, computes MoM growth,
and writes a per-period output table with formula details and null handling.
"""
import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: Path):
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    rows = []
    null_rows = []
    with input_path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for raw_row in reader:
            row = {k: (v.strip() if v is not None else "") for k, v in raw_row.items()}
            actual_spend = row.get("actual_spend", "")
            if actual_spend == "":
                null_rows.append({
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", ""),
                })
                row["actual_spend"] = None
            else:
                try:
                    row["actual_spend"] = float(actual_spend)
                except ValueError:
                    raise ValueError(f"Invalid actual_spend value: {actual_spend}")
            rows.append(row)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    if growth_type != "MoM":
        raise ValueError("Unsupported growth type. Only MoM is supported.")

    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    filtered.sort(key=lambda r: r["period"])
    output = []
    prev_value = None

    for row in filtered:
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row.get("notes", "")

        if actual_spend is None:
            growth = "NULL"
            formula = "N/A"
        elif prev_value is None:
            growth = "N/A"
            formula = "N/A"
            prev_value = actual_spend
        elif prev_value == 0:
            growth = "N/A"
            formula = "N/A"
            prev_value = actual_spend
        else:
            growth = ((actual_spend - prev_value) / prev_value) * 100
            formula = f"(({actual_spend} - {prev_value}) / {prev_value}) * 100"
            prev_value = actual_spend

        output.append({
            "period": period,
            "actual_spend": actual_spend if actual_spend is not None else "NULL",
            "growth": growth,
            "formula": formula,
            "notes": notes,
        })

    return output


def main():
    parser = argparse.ArgumentParser(description="Compute ward/category growth from budget data.")
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--ward", required=True, help="Ward name to filter by.")
    parser.add_argument("--category", required=True, help="Category to filter by.")
    parser.add_argument("--growth-type", required=True, help="Growth type to compute (MoM required).")
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    rows, null_rows = load_dataset(input_path)

    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend rows:")
        for null_row in null_rows:
            print(f"  {null_row['period']} · {null_row['ward']} · {null_row['category']} · {null_row['notes']}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["period", "actual_spend", "growth", "formula", "notes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()

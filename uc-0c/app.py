"""
UC-0C: Ward-level budget growth analysis.

The program intentionally avoids cross-ward and cross-category aggregation.
Missing actual_spend values are flagged rather than silently replaced.
"""

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


def load_dataset(input_path):
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )

        rows = list(reader)

    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Use --growth-type MoM."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "This implementation supports MoM only."
        )

    if ward.strip().lower() in {"all", "all wards", "all-ward"}:
        raise ValueError(
            "Refused: all-ward aggregation is not permitted. "
            "Specify one ward."
        )

    filtered = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    filtered.sort(key=lambda row: row["period"])

    output = []
    previous_spend = None

    for row in filtered:
        period = row["period"]
        actual_text = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if actual_text == "":
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "formula": "NOT COMPUTED",
                "growth": "",
                "status": "NULL - NOT COMPUTED",
                "null_reason": notes or "Reason not provided in notes",
            })

            previous_spend = None
            continue

        actual = float(actual_text)

        if previous_spend is None:
            formula = f"N/A - no previous valid actual_spend for {period}"
            growth = ""
            status = "BASE PERIOD"
        else:
            growth_value = ((actual - previous_spend) / previous_spend) * 100

            formula = (
                f"(({actual:.1f} - {previous_spend:.1f}) / "
                f"{previous_spend:.1f}) * 100"
            )

            growth = f"{growth_value:+.1f}%"
            status = "CALCULATED"

        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual:.1f}",
            "formula": formula,
            "growth": growth,
            "status": status,
            "null_reason": "",
        })

        previous_spend = actual

    return output


def write_output(output, output_path):
    path = Path(output_path)

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ward/category growth without cross-ward aggregation."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows.")
    print(f"Dataset null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes'].strip()}"
        )

    result = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(result, args.output)

    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()

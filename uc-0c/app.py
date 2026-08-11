"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = {"MoM", "YoY"}


def _parse_period(period_value: str) -> datetime:
    return datetime.strptime(period_value.strip(), "%Y-%m")


def load_dataset(input_path: str):
    rows = []
    null_rows = []

    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if any(column not in reader.fieldnames for column in REQUIRED_COLUMNS):
            raise ValueError(f"Input CSV must include columns: {', '.join(REQUIRED_COLUMNS)}")

        for row_number, row in enumerate(reader, start=2):
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            actual_spend_raw = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()
            actual_spend = None
            if actual_spend_raw:
                try:
                    actual_spend = float(actual_spend_raw)
                except ValueError:
                    raise ValueError(f"Invalid actual_spend on row {row_number}: '{actual_spend_raw}'")
            if actual_spend is None:
                null_rows.append({"period": period, "ward": ward, "category": category, "notes": notes})
            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "notes": notes,
                "parsed_period": _parse_period(period),
            })

    return rows, null_rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"Unsupported growth type: {growth_type}. Supported values are {', '.join(VALID_GROWTH_TYPES)}")

    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'")

    filtered.sort(key=lambda row: row["parsed_period"])
    output_rows = []
    previous_row = None

    for row in filtered:
        period = row["period"]
        actual_spend = row["actual_spend"]
        note = ""
        formula = ""
        growth_pct = ""

        if actual_spend is None:
            note = f"NULL actual_spend — {row['notes']}"
        elif previous_row is None:
            note = "No prior period available for growth calculation."
        elif previous_row["actual_spend"] is None:
            note = "Prior period actual_spend is NULL; growth cannot be computed."
        else:
            if growth_type == "MoM":
                formula = f"(( {actual_spend} - {previous_row['actual_spend']} ) / {previous_row['actual_spend']} ) * 100"
                growth_value = ((actual_spend - previous_row["actual_spend"]) / previous_row["actual_spend"]) * 100
                growth_pct = f"{growth_value:+.1f}%"
            else:
                note = "Requested growth type not implemented."

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "NULL" if actual_spend is None else f"{actual_spend:.1f}",
            "growth_type": growth_type,
            "formula": formula,
            "growth_pct": growth_pct,
            "note": note,
        })
        previous_row = row

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to analyse")
    parser.add_argument("--category", required=True, help="Category name to analyse")
    parser.add_argument("--growth-type", required=True, choices=sorted(VALID_GROWTH_TYPES), help="Growth type such as MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"Detected {len(null_rows)} rows with NULL actual_spend before computing growth.")
        for null_row in null_rows:
            print(f"  - {null_row['period']} | {null_row['ward']} | {null_row['category']} | {null_row['notes']}")

    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    with open(args.output, "w", newline="", encoding="utf-8") as output_file:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "formula", "growth_pct", "note"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

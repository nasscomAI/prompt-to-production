"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
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


def load_dataset(input_path: str):
    with open(input_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows = list(reader)

    null_rows = [
        row for row in rows
        if not (row.get("actual_spend") or "").strip()
    ]

    return rows, null_rows


def _parse_amount(value: str):
    stripped = (value or "").strip()
    if not stripped:
        return None
    return float(stripped)


def compute_growth(rows, ward: str, category: str, growth_type: str):
    if not growth_type:
        raise ValueError("growth_type is required; refusing to guess the formula")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth_type: {growth_type}. Only MoM is implemented.")
    if not ward or not category:
        raise ValueError("ward and category are required; refusing broad aggregation")

    scoped_rows = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]
    if not scoped_rows:
        raise ValueError("No rows found for the requested ward and category")

    scoped_rows.sort(key=lambda row: row["period"])
    output_rows = []
    previous_amount = None
    previous_period = ""

    for row in scoped_rows:
        period = row["period"]
        actual_amount = _parse_amount(row["actual_spend"])
        notes = (row.get("notes") or "").strip()

        if actual_amount is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend_lakh": "NULL",
                "growth_type": growth_type,
                "growth_result": "NOT_COMPUTED",
                "formula": f"Cannot compute MoM because actual_spend for {period} is NULL",
                "status": "FLAGGED_NULL",
                "notes": notes or "Null actual_spend with no reason provided",
            })
            previous_amount = None
            previous_period = period
            continue

        if previous_amount is None:
            if previous_period:
                formula = f"Cannot compute MoM because previous actual_spend before {period} is NULL or unavailable"
                result = "NOT_COMPUTED"
                status = "FLAGGED_PREVIOUS_NULL"
            else:
                formula = f"No prior month available for {period}; MoM growth starts from the second observed period"
                result = "NOT_COMPUTED"
                status = "NO_BASE_PERIOD"
        else:
            growth = ((actual_amount - previous_amount) / previous_amount) * 100
            formula = f"(({actual_amount:.1f} - {previous_amount:.1f}) / {previous_amount:.1f}) * 100"
            result = f"{growth:+.1f}%"
            status = "COMPUTED"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend_lakh": f"{actual_amount:.1f}",
            "growth_type": growth_type,
            "growth_result": result,
            "formula": formula,
            "status": status,
            "notes": notes,
        })

        previous_amount = actual_amount
        previous_period = period

    return output_rows


def _write_output(output_path: str, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend_lakh",
        "growth_type",
        "growth_result",
        "formula",
        "status",
        "notes",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="One ward only")
    parser.add_argument("--category", required=True, help="One category only")
    parser.add_argument("--growth-type", required=True, help="Growth type, for example MoM")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    rows, _null_rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    _write_output(args.output, output_rows)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()

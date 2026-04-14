"""
UC-0C app.py
"""
from __future__ import annotations

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


def normalize_key(value: str) -> str:
    return (
        (value or "")
        .strip()
        .lower()
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    with Path(input_path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
            raise ValueError("Input CSV is missing one or more required columns.")

        rows = []
        null_rows = []
        for row in reader:
            row = dict(row)
            actual_spend_raw = (row.get("actual_spend") or "").strip()
            row["budgeted_amount"] = float(row["budgeted_amount"])
            row["actual_spend"] = float(actual_spend_raw) if actual_spend_raw else None
            rows.append(row)
            if row["actual_spend"] is None:
                null_rows.append(row)

    return rows, null_rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if not growth_type:
        raise ValueError("growth_type must be specified explicitly.")
    if growth_type.upper() != "MOM":
        raise ValueError("Only MoM growth is supported for this assignment.")

    ward_key = normalize_key(ward)
    category_key = normalize_key(category)
    filtered = [
        row
        for row in rows
        if normalize_key(row["ward"]) == ward_key and normalize_key(row["category"]) == category_key
    ]

    if not filtered:
        raise ValueError("No rows matched the requested ward and category.")

    filtered.sort(key=lambda row: row["period"])
    results = []

    for index, row in enumerate(filtered):
        previous = filtered[index - 1] if index > 0 else None
        formula = "(current_actual_spend - previous_actual_spend) / previous_actual_spend * 100"
        status = "OK"
        growth_percent = ""
        baseline = ""
        note = (row.get("notes") or "").strip()

        if row["actual_spend"] is None:
            status = "NULL_FLAGGED"
            growth_percent = ""
            baseline = previous["actual_spend"] if previous and previous["actual_spend"] is not None else ""
            note = note or "Null actual_spend row"
        elif previous is None:
            status = "NO_BASELINE"
            baseline = ""
            note = "No previous period available for MoM calculation"
        elif previous["actual_spend"] is None:
            status = "NULL_FLAGGED"
            baseline = ""
            note = (previous.get("notes") or "").strip() or f'Previous period {previous["period"]} has null actual_spend'
        elif previous["actual_spend"] == 0:
            status = "NO_BASELINE"
            baseline = previous["actual_spend"]
            note = f'Previous period {previous["period"]} actual_spend is zero'
        else:
            baseline = previous["actual_spend"]
            growth_value = ((row["actual_spend"] - previous["actual_spend"]) / previous["actual_spend"]) * 100
            growth_percent = f"{growth_value:.1f}%"

        results.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "" if row["actual_spend"] is None else f'{row["actual_spend"]:.1f}',
                "previous_actual_spend": "" if baseline == "" else f"{float(baseline):.1f}",
                "growth_type": "MoM",
                "formula": formula,
                "growth_percent": growth_percent,
                "status": status,
                "note": note,
            }
        )

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="Growth type, for example MoM")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    rows, _null_rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with Path(args.output).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "period",
                "ward",
                "category",
                "actual_spend",
                "previous_actual_spend",
                "growth_type",
                "formula",
                "growth_percent",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()

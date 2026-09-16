"""
UC-0C — Budget Growth Calculator
"""
import argparse
import csv
import sys
from pathlib import Path
from typing import Optional


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
OUTPUT_COLUMNS = [
    "record_type",
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth_type",
    "growth_percent",
    "formula",
    "null_flag",
    "null_reason",
    "notes",
]


def _is_null(value: Optional[str]) -> bool:
    return value is None or not value.strip()


def _refuse_scope(value: str, label: str) -> None:
    folded = value.strip().casefold()
    if not folded:
        raise ValueError(f"--{label} is required")
    if folded in {"all", "all wards", "*", "any"} or "," in value or ";" in value:
        raise ValueError(f"Refusing unsafe {label} scope: specify exactly one {label}")


def load_dataset(input_path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input CSV missing required columns: {', '.join(sorted(missing))}")
        records = list(reader)
    if not records:
        raise ValueError("Budget CSV contains no rows")

    null_rows = []
    for index, row in enumerate(records, start=2):
        for column in REQUIRED_COLUMNS - {"actual_spend", "notes"}:
            if _is_null(row.get(column)):
                raise ValueError(f"Row {index} missing required value for {column}")
        if _is_null(row.get("actual_spend")):
            null_rows.append(row)
        else:
            try:
                float(row["actual_spend"])
                float(row["budgeted_amount"])
            except ValueError as exc:
                raise ValueError(f"Row {index} has malformed numeric data") from exc

    print(f"Null actual_spend rows found before filtering: {len(null_rows)}")
    for row in null_rows:
        print(f"- {row['period']} | {row['ward']} | {row['category']} | {row.get('notes', '')}")
    return records, null_rows


def compute_growth(
    records: list[dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
    null_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    _refuse_scope(ward, "ward")
    _refuse_scope(category, "category")
    if growth_type != "MoM":
        raise ValueError("--growth-type must be specified as MoM; the program will not guess")

    selected = [row for row in records if row["ward"] == ward and row["category"] == category]
    selected.sort(key=lambda row: row["period"])
    if len(selected) != 12:
        raise ValueError(f"Expected 12 rows for requested ward/category, found {len(selected)}")

    output_rows: list[dict[str, str]] = []
    previous_actual: float | None = None
    for row in selected:
        actual_text = row["actual_spend"].strip()
        if _is_null(actual_text):
            growth_percent = "NOT_COMPUTED"
            formula = "NOT_COMPUTED: current actual_spend is null; no imputation performed"
            null_flag = "NULL_ACTUAL_SPEND"
            null_reason = row.get("notes", "")
        else:
            current_actual = float(actual_text)
            if previous_actual is None:
                growth_percent = "NOT_COMPUTED"
                formula = "NOT_COMPUTED: no previous period for MoM comparison"
            elif previous_actual == 0:
                growth_percent = "NOT_COMPUTED"
                formula = "NOT_COMPUTED: previous actual_spend is zero"
            else:
                result = ((current_actual - previous_actual) / previous_actual) * 100
                growth_percent = f"{result:+.1f}%"
                formula = f"(({current_actual:.1f} - {previous_actual:.1f}) / {previous_actual:.1f}) * 100 = {growth_percent}"
            null_flag = ""
            null_reason = ""
            previous_actual = current_actual

        output_rows.append(
            {
                "record_type": "CALCULATION",
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": actual_text,
                "growth_type": growth_type,
                "growth_percent": growth_percent,
                "formula": formula,
                "null_flag": null_flag,
                "null_reason": null_reason,
                "notes": row.get("notes", ""),
            }
        )

    for row in null_rows:
        output_rows.append(
            {
                "record_type": "NULL_AUDIT",
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "growth_type": "NOT_COMPUTED",
                "growth_percent": "NOT_COMPUTED",
                "formula": "NOT_COMPUTED: null actual_spend in complete input dataset",
                "null_flag": "NULL_ACTUAL_SPEND",
                "null_reason": row.get("notes", ""),
                "notes": row.get("notes", ""),
            }
        )
    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="Growth type; supported: MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    try:
        records, null_rows = load_dataset(args.input)
        output_rows = compute_growth(records, args.ward, args.category, args.growth_type, null_rows)
        with Path(args.output).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from pathlib import Path
from typing import Optional


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}
SUPPORTED_GROWTH_TYPES = {"MOM", "YOY"}


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    with Path(input_path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("Dataset is missing one or more required columns")
        rows = list(reader)

    null_rows = [row for row in rows if not (row.get("actual_spend") or "").strip()]
    return rows, null_rows


def _parse_float(value: str) -> Optional[float]:
    text = (value or "").strip()
    if not text:
        return None
    return float(text)


def _validate_scope(ward: str, category: str, growth_type: str) -> str:
    if not growth_type:
        raise ValueError("growth-type is required. Supported values: MoM, YoY")

    normalized_growth = growth_type.strip().upper()
    if normalized_growth not in SUPPORTED_GROWTH_TYPES:
        raise ValueError("Unsupported growth-type. Supported values: MoM, YoY")

    if not ward or ward.strip().lower() in {"all", "any", "*"}:
        raise ValueError("Refusing aggregate ward request. Specify exactly one ward.")

    if not category or category.strip().lower() in {"all", "any", "*"}:
        raise ValueError("Refusing aggregate category request. Specify exactly one category.")

    return normalized_growth


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    normalized_growth = _validate_scope(ward, category, growth_type)
    filtered_rows = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    if not filtered_rows:
        raise ValueError("No rows found for the requested ward and category")

    filtered_rows.sort(key=lambda row: row["period"])
    output_rows: list[dict] = []

    for index, row in enumerate(filtered_rows):
        actual_value = _parse_float(row["actual_spend"])
        baseline_row = None
        baseline_label = ""
        if normalized_growth == "MOM" and index > 0:
            baseline_row = filtered_rows[index - 1]
            baseline_label = baseline_row["period"]
        elif normalized_growth == "YOY":
            baseline_row = next(
                (candidate for candidate in filtered_rows if candidate["period"] == f"{int(row['period'][:4]) - 1}-{row['period'][5:]}"),
                None,
            )
            baseline_label = baseline_row["period"] if baseline_row else ""

        baseline_value = _parse_float(baseline_row["actual_spend"]) if baseline_row else None
        note = row.get("notes", "")
        status = "OK"
        growth_pct = ""

        if actual_value is None:
            status = "FLAGGED_NULL"
            formula = "Growth not computed because current actual_spend is null"
            note = note or "Null actual_spend"
        elif baseline_row is None:
            status = "NO_BASELINE"
            formula = f"No {normalized_growth} baseline available for {row['period']}"
        elif baseline_value is None:
            status = "FLAGGED_NULL"
            formula = f"Growth not computed because baseline actual_spend from {baseline_label} is null"
            note = note or baseline_row.get("notes", "") or "Baseline actual_spend is null"
        elif baseline_value == 0:
            status = "DIVIDE_BY_ZERO"
            formula = f"(({actual_value:.1f} - 0.0) / 0.0) * 100 is undefined"
            note = note or "Baseline actual_spend is zero"
        else:
            growth_value = ((actual_value - baseline_value) / baseline_value) * 100
            growth_pct = f"{growth_value:+.1f}%"
            formula = f"(({actual_value:.1f} - {baseline_value:.1f}) / {baseline_value:.1f}) * 100"

        output_rows.append(
            {
                "period": row["period"],
                "ward": ward,
                "category": category,
                "growth_type": normalized_growth,
                "actual_spend": "" if actual_value is None else f"{actual_value:.1f}",
                "baseline_period": baseline_label,
                "baseline_actual_spend": "" if baseline_value is None else f"{baseline_value:.1f}",
                "formula": formula,
                "growth_pct": growth_pct,
                "status": status,
                "note": note,
            }
        )

    return output_rows


def _write_output(output_path: str, rows: list[dict]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "growth_type",
        "actual_spend",
        "baseline_period",
        "baseline_actual_spend",
        "formula",
        "growth_pct",
        "status",
        "note",
    ]
    with Path(output_path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    rows, _null_rows = load_dataset(args.input)
    result_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    _write_output(args.output, result_rows)
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()

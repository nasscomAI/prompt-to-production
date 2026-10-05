"""UC-0C auditable ward-budget growth calculator."""

import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}
OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend_lakh",
    "prior_actual_spend_lakh",
    "growth_type",
    "growth_percent",
    "formula",
    "status",
    "flag",
    "notes",
]


def load_dataset(input_path: str) -> Tuple[List[Dict[str, object]], List[Dict[str, str]]]:
    """Load and validate budget rows, returning rows and all null-spend records."""
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if not reader.fieldnames:
                raise ValueError("Input CSV is empty or has no header.")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(f"Input CSV is missing required columns: {', '.join(sorted(missing))}.")

            rows: List[Dict[str, object]] = []
            null_rows: List[Dict[str, str]] = []
            for line_number, raw_row in enumerate(reader, start=2):
                row = {column: (raw_row.get(column) or "").strip() for column in REQUIRED_COLUMNS}
                if not row["period"] or not row["ward"] or not row["category"]:
                    raise ValueError(f"Row {line_number} is missing period, ward, or category.")
                try:
                    row["budgeted_amount"] = Decimal(row["budgeted_amount"])
                except InvalidOperation as error:
                    raise ValueError(f"Row {line_number} has an invalid budgeted_amount.") from error

                if row["actual_spend"]:
                    try:
                        row["actual_spend"] = Decimal(row["actual_spend"])
                    except InvalidOperation as error:
                        raise ValueError(f"Row {line_number} has an invalid actual_spend.") from error
                else:
                    row["actual_spend"] = None
                    null_rows.append(
                        {
                            "period": str(row["period"]),
                            "ward": str(row["ward"]),
                            "category": str(row["category"]),
                            "notes": str(row["notes"]),
                        }
                    )
                rows.append(row)
    except OSError as error:
        raise OSError(f"Unable to read input CSV '{input_path}': {error}") from error

    if not rows:
        raise ValueError("Input CSV contains no data rows.")
    return rows, null_rows


def _format_amount(value: object) -> str:
    if value is None:
        return ""
    return format(value, "f")


def _refuse_aggregate(value: str, field_name: str) -> None:
    normalized = value.strip().lower()
    if not normalized or normalized in {"all", "*", "any"} or "," in normalized:
        raise ValueError(
            f"A single exact {field_name} is required; aggregation across {field_name}s is not allowed."
        )


def compute_growth(
    rows: List[Dict[str, object]], ward: str, category: str, growth_type: str
) -> List[Dict[str, str]]:
    """Return an auditable per-period growth table for one ward and category."""
    _refuse_aggregate(ward, "ward")
    _refuse_aggregate(category, "category")
    if growth_type != "MoM":
        raise ValueError("Unsupported growth type. Specify --growth-type MoM; do not infer a method.")

    selected = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    if not selected:
        raise ValueError("No records match the requested ward and category exactly.")
    selected.sort(key=lambda row: str(row["period"]))

    results: List[Dict[str, str]] = []
    previous = None
    generic_formula = "MoM = ((current actual_spend - prior actual_spend) / prior actual_spend) * 100"
    for row in selected:
        current = row["actual_spend"]
        notes = str(row["notes"])
        result = {
            "period": str(row["period"]),
            "ward": ward,
            "category": category,
            "actual_spend_lakh": _format_amount(current),
            "prior_actual_spend_lakh": _format_amount(previous["actual_spend"]) if previous else "",
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": generic_formula,
            "status": "NOT_COMPUTED",
            "flag": "NEEDS_REVIEW",
            "notes": notes,
        }

        if previous is None:
            result["formula"] = f"{generic_formula}; not computed: no prior period available"
        elif current is None:
            reason = "actual_spend is null"
            if notes:
                reason = f"{reason} ({notes})"
            result["formula"] = f"{generic_formula}; not computed: {reason}"
        elif previous["actual_spend"] is None:
            previous_note = str(previous["notes"])
            reason = "prior-period actual_spend is null"
            if previous_note:
                reason = f"{reason} ({previous_note})"
            result["formula"] = f"{generic_formula}; not computed: {reason}"
        elif previous["actual_spend"] == 0:
            result["formula"] = f"{generic_formula}; not computed: prior actual_spend is zero"
        else:
            prior = previous["actual_spend"]
            growth = ((current - prior) / prior * Decimal("100")).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )
            result.update(
                {
                    "growth_percent": f"{growth:+.1f}%",
                    "formula": (
                        f"(({_format_amount(current)} - {_format_amount(prior)}) / "
                        f"{_format_amount(prior)}) * 100 = {growth:+.1f}%"
                    ),
                    "status": "COMPUTED",
                    "flag": "",
                }
            )
        results.append(result)
        previous = row
    return results


def _report_null_rows(null_rows: List[Dict[str, str]]) -> None:
    print(f"Detected {len(null_rows)} null actual_spend row(s):", file=sys.stderr)
    for row in null_rows:
        note = row["notes"] or "no source note supplied"
        print(
            f"- {row['period']} | {row['ward']} | {row['category']} | {note}",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="One exact ward name")
    parser.add_argument("--category", required=True, help="One exact category name")
    parser.add_argument("--growth-type", required=True, help="Explicit calculation method (MoM)")
    parser.add_argument("--output", required=True, help="Path for the growth CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    _report_null_rows(null_rows)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Done. Growth output written to {output_path}")


if __name__ == "__main__":
    main()

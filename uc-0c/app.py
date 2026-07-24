"""Calculate explicit, per-ward/category budget-spend growth from a CSV file."""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path


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
    "growth_type",
    "actual_spend",
    "comparison_period",
    "comparison_actual_spend",
    "formula",
    "growth_percent",
    "status",
    "null_reason",
]


class ValidationError(ValueError):
    """Raised when the input cannot support a verifiable calculation."""


def parse_period(value: str) -> datetime:
    """Parse a YYYY-MM period without accepting partial or guessed dates."""
    try:
        return datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise ValidationError(f"Invalid period {value!r}; expected YYYY-MM.") from exc


def load_dataset(input_path: Path) -> list[dict[str, object]]:
    """Read and validate the source CSV, reporting every null actual-spend row."""
    try:
        with input_path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            headers = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - headers
            if missing:
                raise ValidationError(
                    "Input CSV is missing required columns: " + ", ".join(sorted(missing))
                )

            rows: list[dict[str, object]] = []
            seen_keys: set[tuple[str, str, str]] = set()
            for line_number, raw_row in enumerate(reader, start=2):
                period = (raw_row["period"] or "").strip()
                ward = (raw_row["ward"] or "").strip()
                category = (raw_row["category"] or "").strip()
                notes = (raw_row["notes"] or "").strip()
                if not period or not ward or not category:
                    raise ValidationError(
                        f"Row {line_number} must include period, ward, and category."
                    )
                parse_period(period)

                key = (period, ward, category)
                if key in seen_keys:
                    raise ValidationError(
                        f"Duplicate period/ward/category row at line {line_number}: {key}."
                    )
                seen_keys.add(key)

                raw_actual = (raw_row["actual_spend"] or "").strip()
                actual_spend: float | None
                if raw_actual == "":
                    if not notes:
                        raise ValidationError(
                            f"Null actual_spend at line {line_number} has no reason in notes."
                        )
                    actual_spend = None
                else:
                    try:
                        actual_spend = float(raw_actual)
                    except ValueError as exc:
                        raise ValidationError(
                            f"Invalid actual_spend at line {line_number}: {raw_actual!r}."
                        ) from exc

                rows.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": actual_spend,
                        "notes": notes,
                    }
                )
    except OSError as exc:
        raise ValidationError(f"Cannot read input CSV {input_path}: {exc}") from exc

    null_rows = [row for row in rows if row["actual_spend"] is None]
    print(f"Validated {len(rows)} rows. Null actual_spend rows: {len(null_rows)}.")
    for row in null_rows:
        print(
            "NULL actual_spend: "
            f"{row['period']} | {row['ward']} | {row['category']} | reason: {row['notes']}"
        )
    return rows


def previous_period(period: str, growth_type: str) -> str:
    date = parse_period(period)
    if growth_type == "MoM":
        year, month = (date.year - 1, 12) if date.month == 1 else (date.year, date.month - 1)
    else:  # YoY
        year, month = date.year - 1, date.month
    return f"{year:04d}-{month:02d}"


def number(value: float | None) -> str:
    """Format source values without turning a null into a numeric value."""
    return "" if value is None else f"{value:g}"


def compute_growth(
    rows: list[dict[str, object]], ward: str, category: str, growth_type: str
) -> list[dict[str, str]]:
    """Return one formula-bearing output row per period in one requested scope."""
    selected = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    if not selected:
        raise ValidationError(
            "No rows match the requested ward and category; refusing to broaden the scope."
        )

    selected.sort(key=lambda row: str(row["period"]))
    by_period = {str(row["period"]): row for row in selected}
    output: list[dict[str, str]] = []

    for row in selected:
        period = str(row["period"])
        actual = row["actual_spend"]
        comparison_period = previous_period(period, growth_type)
        comparison = by_period.get(comparison_period)
        comparison_actual = comparison["actual_spend"] if comparison else None
        null_reasons: list[str] = []

        if actual is None:
            null_reasons.append(f"current period: {row['notes']}")
        if comparison is None:
            null_reasons.append(f"comparison period {comparison_period} is unavailable")
        elif comparison_actual is None:
            null_reasons.append(f"comparison period: {comparison['notes']}")

        base = {
            "period": period,
            "ward": ward,
            "category": category,
            "growth_type": growth_type,
            "actual_spend": number(actual if isinstance(actual, float) else None),
            "comparison_period": comparison_period,
            "comparison_actual_spend": number(
                comparison_actual if isinstance(comparison_actual, float) else None
            ),
        }

        if null_reasons:
            base.update(
                {
                    "formula": f"{growth_type}: not computed due to unavailable actual_spend",
                    "growth_percent": "",
                    "status": "not_computable",
                    "null_reason": "; ".join(null_reasons),
                }
            )
        elif comparison_actual == 0:
            base.update(
                {
                    "formula": (
                        f"{growth_type}: ({number(actual)} - 0) / 0 * 100 = not computable"
                    ),
                    "growth_percent": "",
                    "status": "not_computable",
                    "null_reason": "comparison actual_spend is zero; division is undefined",
                }
            )
        else:
            growth = ((actual - comparison_actual) / comparison_actual) * 100
            base.update(
                {
                    "formula": (
                        f"{growth_type}: ({number(actual)} - {number(comparison_actual)}) / "
                        f"{number(comparison_actual)} * 100 = {growth:.1f}%"
                    ),
                    "growth_percent": f"{growth:.1f}",
                    "status": "computed",
                    "null_reason": "",
                }
            )
        output.append(base)
    return output


def write_output(output_path: Path, rows: list[dict[str, str]]) -> None:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        raise ValidationError(f"Cannot write output CSV {output_path}: {exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate scoped MoM or YoY actual-spend growth from ward budget data."
    )
    parser.add_argument("--input", required=True, type=Path, help="Source ward-budget CSV")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=("MoM", "YoY"),
        help="Required comparison formula: MoM or YoY",
    )
    parser.add_argument("--output", required=True, type=Path, help="Per-period output CSV")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
        write_output(args.output, growth_rows)
    except ValidationError as exc:
        parser.error(str(exc))

    print(f"Wrote {len(growth_rows)} per-period rows to {args.output}.")


if __name__ == "__main__":
    main()

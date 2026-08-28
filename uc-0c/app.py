"""Calculate per-period budget growth for one ward and category."""

import argparse
import csv
import sys
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
    "ward",
    "category",
    "period",
    "actual_spend",
    "growth_type",
    "growth_percent",
    "formula",
    "status",
    "null_reason",
]


def load_dataset(input_path):
    """Load and validate the budget CSV before any filtering or calculation."""
    path = Path(input_path)
    if not path.is_file():
        raise ValueError(f"Input file not found: {path}")

    try:
        with path.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            columns = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - columns
            if missing:
                missing_columns = ", ".join(sorted(missing))
                raise ValueError(f"Input CSV is missing columns: {missing_columns}")
            rows = list(reader)
    except OSError as error:
        raise ValueError(f"Could not read input file: {error}") from error

    null_rows = [
        row
        for row in rows
        if row["actual_spend"] is None or not row["actual_spend"].strip()
    ]
    return rows, null_rows


def _growth_periods(rows, growth_type):
    ordered_periods = sorted({row["period"] for row in rows})
    period_index = {period: index for index, period in enumerate(ordered_periods)}
    offset = 1 if growth_type == "MoM" else 12
    return {
        period: ordered_periods[index - offset]
        for period, index in period_index.items()
        if index >= offset
    }


def compute_growth(rows, ward, category, growth_type):
    """Return one output row per period for exactly one ward/category slice."""
    if not ward or not category:
        raise ValueError("Exactly one ward and one category are required.")
    forbidden = {"any", "all", "*"}
    if ward.strip().casefold() in forbidden or category.strip().casefold() in forbidden:
        raise ValueError("Refusing cross-ward or cross-category aggregation.")
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("growth_type must be explicitly selected as MoM or YoY.")

    selected = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    if not selected:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}.")
    if len({row["period"] for row in selected}) != len(selected):
        raise ValueError("Input contains duplicate periods for the requested slice.")

    by_period = {row["period"]: row for row in selected}
    previous_periods = _growth_periods(selected, growth_type)
    results = []
    for period in sorted(by_period):
        row = by_period[period]
        actual_text = row["actual_spend"].strip()
        result = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual_text,
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": "",
            "status": "computed",
            "null_reason": "",
        }
        if not actual_text:
            result["status"] = "null_actual_spend"
            result["null_reason"] = row["notes"].strip()
            print(
                f"NULL actual_spend: {period} | {ward} | {category} | "
                f"reason: {result['null_reason'] or 'not provided'}",
                file=sys.stderr,
            )
            results.append(result)
            continue

        previous_period = previous_periods.get(period)
        if previous_period is None:
            result["status"] = "not_computed"
            result["formula"] = "N/A (no prior period available)"
            results.append(result)
            continue

        previous = by_period[previous_period]
        previous_text = previous["actual_spend"].strip()
        result["formula"] = f"({actual_text} - {previous_text}) / {previous_text} * 100"
        if not previous_text:
            result["status"] = "not_computed"
            result["null_reason"] = previous["notes"].strip()
        else:
            previous_value = float(previous_text)
            if previous_value == 0:
                result["status"] = "not_computed"
                result["null_reason"] = "Previous actual_spend is zero"
            else:
                current_value = float(actual_text)
                result["growth_percent"] = f"{(current_value - previous_value) / previous_value * 100:.1f}%"
        results.append(result)

    return results


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward")
    parser.add_argument("--category", required=True, help="Exactly one category")
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=("MoM", "YoY"),
        help="Explicit growth method: MoM or YoY",
    )
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        rows, null_rows = load_dataset(args.input)
        print(f"Loaded {len(rows)} rows; found {len(null_rows)} null actual_spend values.")
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        with Path(args.output).open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(results)
    except (OSError, ValueError) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

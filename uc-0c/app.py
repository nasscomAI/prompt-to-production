#!/usr/bin/env python3

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# UC-0C — Number That Looks Right
# ============================================================

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

SUPPORTED_GROWTH_TYPES = {
    "MoM",
    "YoY",
}


# ============================================================
# Exceptions
# ============================================================

class GrowthError(Exception):
    """Base exception for UC-0C failures."""


class InvalidInputError(GrowthError):
    """Invalid or unusable input."""


class AggregationError(GrowthError):
    """Illegal aggregation request."""


class GrowthTypeError(GrowthError):
    """Missing or unsupported growth type."""


class NullSpendError(GrowthError):
    """Null actual spend encountered where computation is required."""


class ValidationError(GrowthError):
    """Output or computation validation failure."""


# ============================================================
# Utility functions
# ============================================================

def normalize(value: Any) -> str:
    """Normalize a CSV value without changing substantive content."""
    if value is None:
        return ""
    return str(value).strip()


def is_null(value: Any) -> bool:
    """
    Treat blank CSV actual_spend values as NULL.

    The implementation deliberately does NOT convert NULL to zero.
    """
    return normalize(value) == ""


def parse_amount(value: Any, field_name: str, row_number: int) -> float:
    """Parse a required numeric amount."""
    text = normalize(value)

    if text == "":
        raise InvalidInputError(
            f"Row {row_number}: {field_name} is missing."
        )

    try:
        return float(text)
    except ValueError as exc:
        raise InvalidInputError(
            f"Row {row_number}: {field_name} is not a valid number: {text!r}"
        ) from exc


def validate_period(period: str, row_number: int) -> None:
    """Validate YYYY-MM period format."""
    if len(period) != 7 or period[4] != "-":
        raise InvalidInputError(
            f"Row {row_number}: invalid period {period!r}; "
            "expected YYYY-MM."
        )

    year, month = period.split("-", 1)

    if not (year.isdigit() and month.isdigit()):
        raise InvalidInputError(
            f"Row {row_number}: invalid period {period!r}; "
            "expected YYYY-MM."
        )

    month_number = int(month)

    if month_number < 1 or month_number > 12:
        raise InvalidInputError(
            f"Row {row_number}: invalid month in period {period!r}."
        )


def previous_period(period: str, growth_type: str) -> str:
    """
    Return the comparison period.

    MoM:
        2024-07 -> 2024-06

    YoY:
        2024-07 -> 2023-07
    """
    year = int(period[:4])
    month = int(period[5:7])

    if growth_type == "MoM":
        if month == 1:
            return f"{year - 1:04d}-12"
        return f"{year:04d}-{month - 1:02d}"

    if growth_type == "YoY":
        return f"{year - 1:04d}-{month:02d}"

    raise GrowthTypeError(
        f"Unsupported growth type: {growth_type!r}. "
        f"Supported types: {', '.join(sorted(SUPPORTED_GROWTH_TYPES))}."
    )


def growth_formula(
    growth_type: str,
    current_period: str,
    previous_period_value: str,
) -> str:
    """
    Return the exact formula displayed alongside the result.
    """
    if growth_type == "MoM":
        return (
            f"(({current_period} actual_spend - "
            f"{previous_period_value} actual_spend) / "
            f"{previous_period_value} actual_spend) * 100"
        )

    if growth_type == "YoY":
        return (
            f"(({current_period} actual_spend - "
            f"{previous_period_value} actual_spend) / "
            f"{previous_period_value} actual_spend) * 100"
        )

    raise GrowthTypeError(
        f"Unsupported growth type: {growth_type!r}"
    )


# ============================================================
# Skill: load_dataset
# ============================================================

def load_dataset(input_path: str | Path) -> Dict[str, Any]:
    """
    Skill: load_dataset

    Reads and validates the CSV.

    Returns:
        {
            "rows": [...],
            "null_count": int,
            "null_rows": [...]
        }

    Important:
        NULL actual_spend values are preserved as None.
        They are never converted to zero.
    """

    input_file = Path(input_path)

    # --------------------------------------------------------
    # Invalid input handling
    # --------------------------------------------------------

    if not input_file.exists():
        raise InvalidInputError(
            f"Input CSV does not exist: {input_file}"
        )

    if not input_file.is_file():
        raise InvalidInputError(
            f"Input path is not a file: {input_file}"
        )

    if input_file.suffix.lower() != ".csv":
        raise InvalidInputError(
            f"Input must be a CSV file: {input_file}"
        )

    try:
        with input_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                raise InvalidInputError(
                    "CSV has no header row."
                )

            actual_columns = {
                normalize(column)
                for column in reader.fieldnames
            }

            missing_columns = REQUIRED_COLUMNS - actual_columns

            if missing_columns:
                raise InvalidInputError(
                    "CSV is missing required columns: "
                    + ", ".join(sorted(missing_columns))
                )

            raw_rows = list(reader)

    except UnicodeDecodeError as exc:
        raise InvalidInputError(
            "CSV is not valid UTF-8 text."
        ) from exc
    except csv.Error as exc:
        raise InvalidInputError(
            f"Malformed CSV: {exc}"
        ) from exc
    except OSError as exc:
        raise InvalidInputError(
            f"Unable to read input CSV: {input_file}"
        ) from exc

    if not raw_rows:
        raise InvalidInputError(
            "Input CSV contains no rows."
        )

    # --------------------------------------------------------
    # Validate and normalize rows
    # --------------------------------------------------------

    rows: List[Dict[str, Any]] = []
    null_rows: List[Dict[str, Any]] = []

    for row_number, raw_row in enumerate(raw_rows, start=2):
        period = normalize(raw_row.get("period"))
        ward = normalize(raw_row.get("ward"))
        category = normalize(raw_row.get("category"))
        notes = normalize(raw_row.get("notes"))

        if not period:
            raise InvalidInputError(
                f"Row {row_number}: period is missing."
            )

        if not ward:
            raise InvalidInputError(
                f"Row {row_number}: ward is missing."
            )

        if not category:
            raise InvalidInputError(
                f"Row {row_number}: category is missing."
            )

        validate_period(period, row_number)

        budgeted_amount = parse_amount(
            raw_row.get("budgeted_amount"),
            "budgeted_amount",
            row_number,
        )

        actual_raw = normalize(raw_row.get("actual_spend"))

        if actual_raw == "":
            actual_spend: Optional[float] = None

            null_info = {
                "row_number": row_number,
                "period": period,
                "ward": ward,
                "category": category,
                "reason": notes,
            }

            null_rows.append(null_info)

        else:
            try:
                actual_spend = float(actual_raw)
            except ValueError as exc:
                raise InvalidInputError(
                    f"Row {row_number}: actual_spend is not "
                    f"a valid number: {actual_raw!r}"
                ) from exc

        normalized_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted_amount,
            "actual_spend": actual_spend,
            "notes": notes,
            "_row_number": row_number,
        }

        rows.append(normalized_row)

    # --------------------------------------------------------
    # Required null reporting BEFORE computation
    # --------------------------------------------------------

    print(
        f"Dataset loaded: {len(rows)} rows",
        file=sys.stdout,
    )

    print(
        f"NULL actual_spend count: {len(null_rows)}",
        file=sys.stdout,
    )

    for null_row in null_rows:
        print(
            "NULL row: "
            f"{null_row['period']} | "
            f"{null_row['ward']} | "
            f"{null_row['category']} | "
            f"reason: {null_row['reason'] or '[no reason provided]'}",
            file=sys.stdout,
        )

    return {
        "rows": rows,
        "null_count": len(null_rows),
        "null_rows": null_rows,
    }


# ============================================================
# Skill: compute_growth
# ============================================================

def compute_growth(
    dataset: Dict[str, Any],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth

    Computes growth only for the explicitly requested ward and
    category.

    Returns one row per period with:
        ward
        category
        period
        actual_spend
        growth
        formula
        status
        null_reason

    NULL actual_spend values are flagged and never treated as zero.
    """

    # --------------------------------------------------------
    # Validate skill inputs
    # --------------------------------------------------------

    if not isinstance(dataset, dict):
        raise InvalidInputError(
            "dataset must be the validated dataset returned by load_dataset."
        )

    if "rows" not in dataset:
        raise InvalidInputError(
            "Validated dataset does not contain rows."
        )

    ward = normalize(ward)
    category = normalize(category)
    growth_type = normalize(growth_type)

    if not ward:
        raise InvalidInputError(
            "ward is required."
        )

    if not category:
        raise InvalidInputError(
            "category is required."
        )

    # --------------------------------------------------------
    # Missing growth type: REFUSE, never guess.
    # --------------------------------------------------------

    if not growth_type:
        raise GrowthTypeError(
            "Growth type was not specified. "
            "Please provide --growth-type, for example MoM."
        )

    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise GrowthTypeError(
            f"Unsupported growth type {growth_type!r}. "
            "Supported values are MoM and YoY."
        )

    # --------------------------------------------------------
    # Scope enforcement
    # --------------------------------------------------------

    rows = dataset["rows"]

    scoped_rows = [
        row
        for row in rows
        if row["ward"] == ward
        and row["category"] == category
    ]

    if not scoped_rows:
        raise InvalidInputError(
            f"No rows found for ward={ward!r}, "
            f"category={category!r}."
        )

    # --------------------------------------------------------
    # Prevent accidental aggregation.
    #
    # The skill explicitly filters to one ward + one category.
    # It never sums across either dimension.
    # --------------------------------------------------------

    unique_wards = {
        row["ward"]
        for row in scoped_rows
    }

    unique_categories = {
        row["category"]
        for row in scoped_rows
    }

    if unique_wards != {ward}:
        raise AggregationError(
            "Illegal cross-ward aggregation detected."
        )

    if unique_categories != {category}:
        raise AggregationError(
            "Illegal cross-category aggregation detected."
        )

    # --------------------------------------------------------
    # Sort by chronological period.
    # --------------------------------------------------------

    scoped_rows.sort(
        key=lambda row: row["period"]
    )

    # --------------------------------------------------------
    # Index by period.
    # --------------------------------------------------------

    by_period: Dict[str, Dict[str, Any]] = {}

    for row in scoped_rows:
        period = row["period"]

        if period in by_period:
            raise ValidationError(
                f"Duplicate period {period!r} for "
                f"{ward!r} / {category!r}."
            )

        by_period[period] = row

    # --------------------------------------------------------
    # Compute per-period growth.
    # --------------------------------------------------------

    results: List[Dict[str, Any]] = []

    for row in scoped_rows:
        period = row["period"]
        actual_spend = row["actual_spend"]

        comparison_period = previous_period(
            period,
            growth_type,
        )

        formula = growth_formula(
            growth_type,
            period,
            comparison_period,
        )

        # ----------------------------------------------------
        # Current period is NULL.
        # ----------------------------------------------------

        if actual_spend is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "",
                "growth": "",
                "formula": formula,
                "status": "FLAGGED_NULL",
                "null_reason": row["notes"],
            })

            continue

        # ----------------------------------------------------
        # First period / comparison period absent.
        #
        # For MoM, January has no December-2023 row in the
        # supplied 2024 dataset.
        # ----------------------------------------------------

        previous_row = by_period.get(comparison_period)

        if previous_row is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": actual_spend,
                "growth": "",
                "formula": formula,
                "status": "NOT_COMPUTED_NO_COMPARISON",
                "null_reason": "",
            })

            continue

        previous_actual = previous_row["actual_spend"]

        # ----------------------------------------------------
        # Previous period is NULL.
        #
        # Never treat it as zero.
        # ----------------------------------------------------

        if previous_actual is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": actual_spend,
                "growth": "",
                "formula": formula,
                "status": "FLAGGED_PREVIOUS_NULL",
                "null_reason": previous_row["notes"],
            })

            continue

        # ----------------------------------------------------
        # Division by zero.
        # ----------------------------------------------------

        if previous_actual == 0:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": actual_spend,
                "growth": "",
                "formula": formula,
                "status": "NOT_COMPUTED_DIVISION_BY_ZERO",
                "null_reason": "",
            })

            continue

        # ----------------------------------------------------
        # Actual growth calculation.
        #
        # Growth % =
        # ((current - previous) / previous) * 100
        # ----------------------------------------------------

        growth = (
            (actual_spend - previous_actual)
            / previous_actual
        ) * 100.0

        results.append({
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual_spend,
            "growth": growth,
            "formula": formula,
            "status": "COMPUTED",
            "null_reason": "",
        })

    # --------------------------------------------------------
    # Validate that this remains a per-period table.
    # --------------------------------------------------------

    if not results:
        raise ValidationError(
            "Growth computation produced no output rows."
        )

    if any(
        result["ward"] != ward
        or result["category"] != category
        for result in results
    ):
        raise AggregationError(
            "Output escaped the requested ward/category scope."
        )

    return results


# ============================================================
# Output validation
# ============================================================

def validate_output(
    results: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> None:
    """
    Final enforcement validation before writing the CSV.
    """

    if not results:
        raise ValidationError(
            "Cannot write an empty growth result."
        )

    if not growth_type:
        raise GrowthTypeError(
            "Growth type is missing."
        )

    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise GrowthTypeError(
            f"Unsupported growth type: {growth_type!r}"
        )

    for result in results:
        # Scope
        if result["ward"] != ward:
            raise AggregationError(
                "Output contains a ward outside the requested scope."
            )

        if result["category"] != category:
            raise AggregationError(
                "Output contains a category outside the requested scope."
            )

        # Formula must always be present.
        if not normalize(result.get("formula")):
            raise ValidationError(
                f"Period {result['period']}: formula is missing."
            )

        # Every NULL row must be flagged.
        if result["status"] == "FLAGGED_NULL":
            if result["actual_spend"] != "":
                raise ValidationError(
                    f"Period {result['period']}: NULL row has "
                    "a fabricated actual_spend value."
                )

            if not normalize(result["null_reason"]):
                raise ValidationError(
                    f"Period {result['period']}: NULL row has "
                    "no reason from notes."
                )

            if normalize(result["growth"]):
                raise ValidationError(
                    f"Period {result['period']}: growth was computed "
                    "for a NULL actual_spend."
                )

        # Previous NULL must also never be treated as zero.
        if result["status"] == "FLAGGED_PREVIOUS_NULL":
            if normalize(result["growth"]):
                raise ValidationError(
                    f"Period {result['period']}: growth was computed "
                    "despite a NULL comparison value."
                )

            if not normalize(result["null_reason"]):
                raise ValidationError(
                    f"Period {result['period']}: previous NULL "
                    "reason is missing."
                )


# ============================================================
# CSV writer
# ============================================================

def write_output(
    output_path: str | Path,
    results: List[Dict[str, Any]],
) -> None:
    """Write the validated per-period growth table."""

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth",
        "formula",
        "status",
        "null_reason",
    ]

    try:
        with output_file.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for result in results:
                row = dict(result)

                # Keep CSV numeric values readable.
                if isinstance(row["actual_spend"], float):
                    row["actual_spend"] = (
                        f"{row['actual_spend']:.10g}"
                    )

                if isinstance(row["growth"], float):
                    row["growth"] = (
                        f"{row['growth']:.1f}%"
                    )

                writer.writerow(row)

    except OSError as exc:
        raise GrowthError(
            f"Unable to write output CSV: {output_file}"
        ) from exc


# ============================================================
# CLI
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input ward budget CSV.",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyze.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyze.",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        choices=sorted(SUPPORTED_GROWTH_TYPES),
        help="Growth formula to use: MoM or YoY.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path.",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================

def main() -> int:
    try:
        args = parse_args()

        # ----------------------------------------------------
        # Explicit growth type enforcement.
        #
        # argparse makes --growth-type mandatory, so a missing
        # value cannot silently become MoM or YoY.
        # ----------------------------------------------------

        if not args.growth_type:
            raise GrowthTypeError(
                "Growth type was not specified. "
                "Please provide --growth-type; never guess."
            )

        # ----------------------------------------------------
        # Load and validate dataset.
        #
        # This reports all NULL rows BEFORE computation.
        # ----------------------------------------------------

        dataset = load_dataset(
            args.input
        )

        # ----------------------------------------------------
        # Compute only requested ward + category.
        # ----------------------------------------------------

        results = compute_growth(
            dataset=dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )

        # ----------------------------------------------------
        # Final enforcement validation.
        # ----------------------------------------------------

        validate_output(
            results=results,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )

        # ----------------------------------------------------
        # Write required output.
        # ----------------------------------------------------

        write_output(
            output_path=args.output,
            results=results,
        )

        print(
            f"Growth calculation completed successfully: "
            f"{args.output}"
        )

        print(
            f"Scope: {args.ward} | {args.category} | "
            f"{args.growth_type}"
        )

        print(
            f"Output rows: {len(results)}"
        )

        return 0

    except GrowthError as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    except KeyboardInterrupt:
        print(
            "ERROR: operation cancelled.",
            file=sys.stderr,
        )
        return 130

    except Exception as exc:
        # Fail closed: never produce an apparently valid result
        # after an unexpected failure.
        print(
            f"ERROR: unexpected failure: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

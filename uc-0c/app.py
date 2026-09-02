"""
UC-0C - Number That Looks Right

Budget Growth Analysis Agent

Purpose:
    Calculate period-by-period growth for one explicitly selected
    ward and category.

Safety rules:
    1. Never aggregate across wards or categories.
    2. Never silently convert NULL to zero.
    3. Always report NULL rows before calculation.
    4. Always show the formula used.
    5. Never guess the growth type.
    6. Never calculate growth when the required comparison value is missing.
"""

import argparse
import csv
import sys
from datetime import datetime


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

SUPPORTED_GROWTH_TYPES = {"MOM", "YOY"}

AGGREGATION_WORDS = {
    "all",
    "all wards",
    "all-wards",
    "any",
}

CATEGORY_AGGREGATION_WORDS = {
    "all",
    "all categories",
    "all-categories",
    "any",
}


def normalize_text(value):
    """
    Normalize whitespace and common UTF-8/console encoding artifacts.
    """

    if value is None:
        return ""

    text = str(value)

    replacements = {
        "â€“": "–",
        "â€”": "—",
        "â€˜": "‘",
        "â€™": "’",
        "â€œ": "“",
        "â€\x9d": "”",
        "\ufeff": "",
        "\xa0": " ",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return " ".join(text.split())


def parse_period(period):
    """
    Convert YYYY-MM into a real date for reliable chronological sorting.
    """

    try:
        return datetime.strptime(
            period,
            "%Y-%m"
        )
    except ValueError:
        raise ValueError(
            f"Invalid period '{period}'. "
            "Expected format YYYY-MM."
        )


def parse_amount(value, field_name, period):
    """
    Convert a numeric value to float.

    Empty actual_spend is intentionally treated as NULL.
    """

    if value is None or value == "":
        return None

    try:
        return float(value)
    except ValueError:
        raise ValueError(
            f"Invalid numeric {field_name} value "
            f"'{value}' for period {period}."
        )


def load_dataset(input_path):
    """
    Load and validate the supplied budget CSV.

    Returns:
        rows       -> validated dataset
        null_rows  -> every row where actual_spend is NULL
    """

    try:
        with open(
            input_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV file is empty or has no header."
                )

            reader.fieldnames = [
                normalize_text(column)
                for column in reader.fieldnames
            ]

            missing_columns = [
                column
                for column in REQUIRED_COLUMNS
                if column not in reader.fieldnames
            ]

            if missing_columns:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                )

            rows = []

            for row_number, row in enumerate(
                reader,
                start=2
            ):

                cleaned = {
                    key: normalize_text(value)
                    for key, value in row.items()
                }

                # Required text fields
                for field in [
                    "period",
                    "ward",
                    "category",
                ]:
                    if not cleaned.get(field):
                        raise ValueError(
                            f"Missing {field} "
                            f"at CSV row {row_number}."
                        )

                # Validate period
                parse_period(
                    cleaned["period"]
                )

                # Validate budgeted amount
                parse_amount(
                    cleaned["budgeted_amount"],
                    "budgeted_amount",
                    cleaned["period"],
                )

                # actual_spend is allowed to be NULL.
                if cleaned["actual_spend"] != "":
                    parse_amount(
                        cleaned["actual_spend"],
                        "actual_spend",
                        cleaned["period"],
                    )

                rows.append(cleaned)

    except FileNotFoundError:
        raise ValueError(
            f"Input file not found: {input_path}"
        )

    except OSError as exc:
        raise ValueError(
            f"Unable to read input file: {exc}"
        )

    if not rows:
        raise ValueError(
            "CSV contains no data rows."
        )

    null_rows = [
        row
        for row in rows
        if row["actual_spend"] == ""
    ]

    return rows, null_rows


def calculate_mom_growth(current, previous):
    """
    Calculate Month-over-Month growth.

    Formula:
        ((Current Month - Previous Month)
         / Previous Month) * 100
    """

    if current is None or previous is None:
        return (
            None,
            "NOT COMPUTED - required value is NULL"
        )

    if previous == 0:
        return (
            None,
            "NOT COMPUTED - previous value is zero"
        )

    growth = (
        (current - previous)
        / previous
        * 100
    )

    formula = (
        f"(({current:.2f} - {previous:.2f}) "
        f"/ {previous:.2f}) * 100"
    )

    return growth, formula


def calculate_yoy_growth(rows):
    """
    YoY requires the same month from the previous year.

    The supplied assignment dataset contains only 2024,
    so YoY cannot be calculated responsibly.
    """

    years = {
        row["period"][:4]
        for row in rows
    }

    if len(years) < 2:
        raise ValueError(
            "YoY growth cannot be computed because "
            "the supplied dataset contains only one year "
            f"({', '.join(sorted(years))})."
        )


def compute_growth(
    rows,
    ward,
    category,
    growth_type
):
    """
    Calculate growth for exactly one ward and one category.
    """

    growth_type = normalize_text(
        growth_type
    ).upper()

    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            "Unsupported growth type. "
            "Use MoM or YoY."
        )

    matching_rows = [
        row
        for row in rows
        if row["ward"] == ward
        and row["category"] == category
    ]

    if not matching_rows:
        raise ValueError(
            f"No data found for ward '{ward}' "
            f"and category '{category}'."
        )

    matching_rows.sort(
        key=lambda row: parse_period(
            row["period"]
        )
    )

    if growth_type == "YOY":
        calculate_yoy_growth(
            matching_rows
        )

    output = []

    # --------------------------------------------------
    # MoM calculation
    # --------------------------------------------------

    if growth_type == "MOM":

        previous_value = None
        previous_period = None

        for row in matching_rows:

            current_value = parse_amount(
                row["actual_spend"],
                "actual_spend",
                row["period"],
            )

            # ------------------------------------------
            # NULL current value
            # ------------------------------------------

            if current_value is None:

                output.append(
                    {
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "previous_period": (
                            previous_period or ""
                        ),
                        "previous_actual_spend": (
                            ""
                            if previous_value is None
                            else f"{previous_value:.2f}"
                        ),
                        "actual_spend": "",
                        "growth_type": "MoM",
                        "formula": (
                            "NOT COMPUTED - "
                            "actual_spend is NULL"
                        ),
                        "growth": "",
                        "status": "FLAGGED_NULL",
                        "notes": row["notes"],
                    }
                )

                # A NULL month breaks the continuous
                # month-to-month comparison.
                previous_value = None
                previous_period = None

                continue

            # ------------------------------------------
            # First valid period
            # ------------------------------------------

            if previous_value is None:

                output.append(
                    {
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "previous_period": "",
                        "previous_actual_spend": "",
                        "actual_spend": (
                            f"{current_value:.2f}"
                        ),
                        "growth_type": "MoM",
                        "formula": (
                            "NOT COMPUTED - "
                            "no valid previous period value"
                        ),
                        "growth": "",
                        "status": "NOT_COMPUTED",
                        "notes": row["notes"],
                    }
                )

                previous_value = current_value
                previous_period = row["period"]

                continue

            # ------------------------------------------
            # Normal MoM calculation
            # ------------------------------------------

            growth, formula = calculate_mom_growth(
                current_value,
                previous_value,
            )

            if growth is None:

                status = "NOT_COMPUTED"
                growth_value = ""

            else:

                status = "COMPUTED"
                growth_value = (
                    f"{growth:+.1f}%"
                )

            output.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_period": previous_period,
                    "previous_actual_spend": (
                        f"{previous_value:.2f}"
                    ),
                    "actual_spend": (
                        f"{current_value:.2f}"
                    ),
                    "growth_type": "MoM",
                    "formula": formula,
                    "growth": growth_value,
                    "status": status,
                    "notes": row["notes"],
                }
            )

            previous_value = current_value
            previous_period = row["period"]

    return output


def write_output(output, output_path):
    """
    Write the detailed growth analysis to CSV.
    """

    fieldnames = [
        "period",
        "ward",
        "category",
        "previous_period",
        "previous_actual_spend",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
        "notes",
    ]

    try:
        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(output)

    except OSError as exc:
        raise ValueError(
            f"Unable to write output file: {exc}"
        )


def print_summary(
    rows,
    null_rows,
    output,
    ward,
    category,
    growth_type,
):
    """
    Print a clear validation and calculation summary.
    """

    computed = sum(
        1
        for row in output
        if row["status"] == "COMPUTED"
    )

    flagged_null = sum(
        1
        for row in output
        if row["status"] == "FLAGGED_NULL"
    )

    not_computed = sum(
        1
        for row in output
        if row["status"] == "NOT_COMPUTED"
    )

    print()
    print("=" * 65)
    print("UC-0C BUDGET GROWTH ANALYSIS")
    print("=" * 65)

    print(f"Input rows          : {len(rows)}")
    print(f"NULL actual_spend   : {len(null_rows)}")
    print(f"Ward                : {ward}")
    print(f"Category            : {category}")
    print(f"Growth type         : {growth_type}")

    print("-" * 65)
    print(f"Computed rows       : {computed}")
    print(f"NULL rows flagged   : {flagged_null}")
    print(f"Not computed        : {not_computed}")

    if null_rows:
        print()
        print("NULL VALIDATION")
        print("-" * 65)

        for row in null_rows:
            print(
                f"{row['period']} | "
                f"{row['ward']} | "
                f"{row['category']} | "
                f"Reason: {row['notes']}"
            )

    print("-" * 65)
    print("Aggregation status  : REFUSED for cross-ward/category requests")
    print("NULL handling       : NULL is never treated as zero")
    print("Formula visibility  : ENABLED")
    print("=" * 65)
    print()


def validate_request(ward, category, growth_type):
    """
    Enforce explicit analysis boundaries.
    """

    if not ward:
        raise ValueError(
            "Ward is required. "
            "Specify exactly one ward."
        )

    if not category:
        raise ValueError(
            "Category is required. "
            "Specify exactly one category."
        )

    if ward.lower() in AGGREGATION_WORDS:
        raise ValueError(
            "REFUSED: all-ward aggregation is not permitted. "
            "Specify exactly one ward."
        )

    if category.lower() in CATEGORY_AGGREGATION_WORDS:
        raise ValueError(
            "REFUSED: cross-category aggregation is not permitted. "
            "Specify exactly one category."
        )

    if not growth_type:
        raise ValueError(
            "Growth type is required. "
            "Specify --growth-type MoM or YoY. "
            "The agent will never guess the formula."
        )

    if growth_type.upper() not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            "Invalid growth type. "
            "Supported values are MoM and YoY."
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Calculate verifiable period-by-period "
            "budget growth for one ward and one category."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward budget CSV",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward to analyze",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category to analyze",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        choices=[
            "MoM",
            "mom",
            "YoY",
            "yoy",
        ],
        help=(
            "Explicit growth method: MoM or YoY"
        ),
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path",
    )

    args = parser.parse_args()

    ward = normalize_text(
        args.ward
    )

    category = normalize_text(
        args.category
    )

    growth_type = normalize_text(
        args.growth_type
    ).upper()

    try:

        # ----------------------------------------------
        # Validate request before touching calculations
        # ----------------------------------------------

        validate_request(
            ward,
            category,
            growth_type,
        )

        # ----------------------------------------------
        # Load complete dataset
        # ----------------------------------------------

        rows, null_rows = load_dataset(
            args.input
        )

        print(
            f"Loaded {len(rows)} rows successfully."
        )

        # ----------------------------------------------
        # REQUIRED: report ALL NULL rows first
        # ----------------------------------------------

        print(
            f"NULL actual_spend rows found: "
            f"{len(null_rows)}"
        )

        for row in null_rows:

            print(
                f"FLAGGED NULL: "
                f"{row['period']} | "
                f"{row['ward']} | "
                f"{row['category']} | "
                f"Reason: {row['notes']}"
            )

        # ----------------------------------------------
        # Compute only requested ward/category
        # ----------------------------------------------

        output = compute_growth(
            rows,
            ward,
            category,
            growth_type,
        )

        # ----------------------------------------------
        # Write detailed result
        # ----------------------------------------------

        write_output(
            output,
            args.output,
        )

        # ----------------------------------------------
        # Display final validation summary
        # ----------------------------------------------

        print_summary(
            rows,
            null_rows,
            output,
            ward,
            category,
            growth_type,
        )

        print(
            f"Output written to: {args.output}"
        )

    except ValueError as exc:

        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
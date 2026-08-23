"""
UC-0C — Number That Looks Right
Budget growth calculator built using the RICE + agents.md + skills.md workflow.
"""

import argparse
import csv
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

ALLOWED_GROWTH_TYPES = {"MoM"}


def load_dataset(input_path):
    """Load and validate the budget CSV."""

    try:
        with open(input_path, "r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header row.")

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)

            if missing:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(sorted(missing))
                )

            rows = list(reader)

    except (OSError, csv.Error) as exc:
        raise ValueError(
            f"Unable to read input dataset: {type(exc).__name__}."
        ) from exc

    null_rows = []

    for row in rows:
        actual = row.get("actual_spend")

        if actual is None or not str(actual).strip():
            null_rows.append(row)

    return rows, null_rows


def calculate_mom(current, previous):
    """Calculate month-over-month growth percentage."""

    if current is None or previous is None:
        return None

    if previous == 0:
        return None

    return ((current - previous) / previous) * 100


def compute_growth(rows, ward, category, growth_type):
    """
    Compute growth for exactly one ward and one category.

    No aggregation across wards or categories is performed.
    """

    if not growth_type:
        raise ValueError(
            "Growth type must be explicitly specified."
        )

    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            f"Supported type: MoM."
        )

    # Explicitly reject aggregate requests.
    if ward.strip().lower() in {"all", "all wards", "all-wards"}:
        raise ValueError(
            "All-ward aggregation is not permitted."
        )

    if category.strip().lower() in {"all", "all categories", "all-categories"}:
        raise ValueError(
            "Cross-category aggregation is not permitted."
        )

    filtered = [
        row
        for row in rows
        if row.get("ward") == ward
        and row.get("category") == category
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' "
            f"and category '{category}'."
        )

    # Sort by YYYY-MM period.
    filtered.sort(key=lambda row: row.get("period", ""))

    results = []
    previous_actual = None
    previous_period = None

    for row in filtered:
        period = row.get("period", "")
        actual_text = row.get("actual_spend")

        # NULL actual spend.
        if actual_text is None or not str(actual_text).strip():
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_type": growth_type,
                    "formula": "",
                    "growth": "",
                    "status": (
                        "NOT_COMPUTED: NULL actual_spend — "
                        + (row.get("notes") or "No reason provided.")
                    ),
                }
            )

            # A null current value cannot become the previous
            # value for the next month's calculation.
            previous_actual = None
            previous_period = period
            continue

        try:
            current_actual = float(actual_text)
        except (TypeError, ValueError):
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_text,
                    "growth_type": growth_type,
                    "formula": "",
                    "growth": "",
                    "status": "NOT_COMPUTED: Invalid actual_spend.",
                }
            )

            previous_actual = None
            previous_period = period
            continue

        # First month has no previous month.
        if previous_actual is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current_actual,
                    "growth_type": growth_type,
                    "formula": "N/A — no previous month actual_spend",
                    "growth": "",
                    "status": "NOT_COMPUTED: First period.",
                }
            )

        elif previous_actual == 0:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current_actual,
                    "growth_type": growth_type,
                    "formula": (
                        f"(({current_actual} - {previous_actual}) "
                        f"/ {previous_actual}) * 100"
                    ),
                    "growth": "",
                    "status": (
                        "NOT_COMPUTED: Previous actual_spend is zero."
                    ),
                }
            )

        else:
            growth = calculate_mom(
                current_actual,
                previous_actual,
            )

            formula = (
                f"(({current_actual} - {previous_actual}) "
                f"/ {previous_actual}) * 100"
            )

            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": current_actual,
                    "growth_type": growth_type,
                    "formula": formula,
                    "growth": f"{growth:.2f}%",
                    "status": "COMPUTED",
                }
            )

        previous_actual = current_actual
        previous_period = period

    return results


def write_output(output_path, results):
    """Write the growth results to CSV."""

    output_fields = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=output_fields,
        )

        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward name",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category name",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type, e.g. MoM",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV",
    )

    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)

        # Report null rows before computation.
        print(f"Dataset rows loaded: {len(rows)}")
        print(f"Null actual_spend rows: {len(null_rows)}")

        for row in null_rows:
            print(
                f"NULL: {row.get('period')} | "
                f"{row.get('ward')} | "
                f"{row.get('category')} | "
                f"{row.get('notes', '')}"
            )

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(
            args.output,
            results,
        )

        print(
            f"Done. Results written to {args.output}"
        )

    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)

    except OSError as exc:
        print(
            f"ERROR: Unable to write output: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()